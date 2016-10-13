# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description:  实现主要的功能
"""
from pymongo import MongoClient
from bson import ObjectId, json_util
import tornado.escape
import tornado.web
import config
import os
import datetime
import uuid
import re
import hashlib

client = MongoClient('mongodb://localhost:27017/')  # 创建连接


class BaseHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie('user')


class IndexHandelr(BaseHandler):
    def get(self):
        self.render('index.html')


class UploadHandler(BaseHandler):
    def get(self):
        self.render('upload.html')

    # 处理文件上传
    @tornado.web.authenticated
    def post(self):
        db = client.picture_manager
        file_metas = self.request.files['files']
        tags = self.get_argument('tags')  # 获取到客户端提交的tag标签
        wrong_file = []  # 保存各种原因未能上传成功的图

        source_files = []
        preview_files = []

        for file_meta in file_metas:  # 归类到两个数组中  array1 : 源文件   array2 : 预览文件
            file_name = file_meta['filename']
            postfix = file_name[file_name.rindex('.') - 4: file_name.rindex('.')]

            if postfix == config.PREVIEW_FILE_POSTFIX:
                preview_files.append(file_meta)
            else:
                source_files.append(file_meta)

        for source_file in source_files:  # 遍历所有文件
            file_name = source_file['filename'][0:source_file['filename'].rindex('.')]
            expect_preview_file = file_name + config.PREVIEW_FILE_POSTFIX
            preview_file = UploadHandler.find_preview_file_by_filename(expect_preview_file,
                                                                       preview_files)
            # 在预览文件中查找有没有源文件对应的预览文件 ，没有则不上传，加入到错误文件列表中
            if preview_file:
                source_file_name = source_file['filename']
                preview_file_name = preview_file['filename']

                base_path = config.FILE_UPLOAD_PATH + "\\" + datetime.datetime.now().strftime(
                    "%Y") + "\\" + datetime.datetime.now().strftime('%m')
                if os.path.exists(base_path):
                    pass
                else:
                    os.makedirs(base_path)

                source_file_path = os.path.join(base_path, source_file_name)
                preview_file_path = os.path.join(base_path, preview_file_name)

                if os.path.exists(source_file_path):
                    source_file_path = source_file_path[0:source_file_path.rindex(".")] + "_uuid" + str(uuid.uuid1())[
                                                                                                    0:8] + source_file_path[
                                                                                                           source_file_path.rindex(
                                                                                                               "."):]
                    preview_file_path = preview_file_path[0:preview_file_path.rindex(".")] + "_uuid" + str(
                        uuid.uuid1())[
                                                                                                       0:8] + preview_file_path[
                                                                                                              preview_file_path.rindex(
                                                                                                                  "."):]

                with open(source_file_path, 'wb') as up:
                    up.write(source_file['body'])
                up.close()

                with open(preview_file_path, 'wb') as up:
                    up.write(preview_file['body'])
                up.close()

                # 构建源文件数据库内容，并且写入数据库
                source_picture = {"upload_date": datetime.datetime.now().strftime('%Y-%m-%d'),
                                  "file_path": source_file_path, "preview_file_path": preview_file_path, "tag": tags,
                                  "file_name": source_file_name,
                                  "file_length": UploadHandler.get_file_length(source_file['body'])}

                db.picture.insert_one(source_picture)
            else:
                wrong_file.append(source_file)

            if len(wrong_file) < 1:
                self.write(tornado.web.escape.json_encode({'message': 'successful'}))
            else:
                self.write(tornado.web.escape.json_encode({'message': len(wrong_file)}))

            self.finish()

    # 线性查找源文件的预览文件
    @staticmethod
    def find_preview_file_by_filename(expect_preview_file, preview_files):
        for preview_file in preview_files:
            if preview_file['filename'].startswith(expect_preview_file):
                return preview_file
        return None

    # 解析文件大小，并且返回用于现实的字符串
    @staticmethod
    def get_file_length(file):
        length_kb = len(file) / 1024
        if length_kb < 1024:
            return str(length_kb) + "KB"
        elif length_kb < 1024 * 1024:
            return str(length_kb / 1024) + "MB"
        else:
            return str(length_kb / (1024 * 1024)) + "GB"


class SearchHandler(BaseHandler):
    @tornado.web.asynchronous
    @tornado.web.authenticated
    def post(self):
        db = client.picture_manager
        search_keys_str = self.get_argument("search_keys")

        if not search_keys_str or re.match('^\W', search_keys_str):
            self.write(json_util.dumps({"message": "非法关键字"}))
            self.finish()
            return

        search_keys_str_array = []
        for val in search_keys_str:
            if re.match('[\w | \s]+', val):
                search_keys_str_array.append("%s" % val)
            else:
                search_keys_str_array.append("\\%s" % val)

        search_keys = "".join(search_keys_str_array).split(" ")  # 查询关键字

        page = int(self.get_argument('page', 0) or 0)  # 页数
        start_date = self.get_argument("start_date")  # 开始日期
        end_date = self.get_argument("end_date")  # 结束如期

        # 查询条件拼接
        query_post = {
            "$and": []
        }

        if start_date and end_date:
            query_post['$and'].append({"upload_date": {"$gte": start_date}})
            query_post['$and'].append({"upload_date": {"$lt": end_date}})

        search_key_or = {"$or": []}
        for search_key in search_keys:
            search_key_or['$or'].append({"file_name": {"$regex": search_key, "$options": "i"}})
            search_key_or['$or'].append({"tag": {"$regex": search_key, "$options": "i"}})

        query_post['$and'].append(search_key_or)

        result = db.picture.find(query_post).limit(config.EACH_PAGE_ITEM).skip(page * config.EACH_PAGE_ITEM)

        if result.count(with_limit_and_skip=True) > 0:
            self.write(json_util.dumps({"message": "succ", "data": result}))
        else:
            self.write(json_util.dumps({"message": "没有更多了"}))
        self.finish()


class ImageHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, id):
        image_id = ObjectId(id)
        db = client.picture_manager
        picture = db.picture.find_one({"_id": image_id})
        self.set_header("Content-Type", "image/jpg")
        if os.path.exists(picture['preview_file_path']):
            self.write(open(picture['preview_file_path'], "rb").read())
        else:
            self.write(
                open(os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static/internal/404.jpg'), "rb").read())
        self.finish()


class PictureHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, id):
        image_id = ObjectId(id)
        db = client.picture_manager
        picture = db.picture.find_one({"_id": image_id})
        if picture:
            self.render(template_name='picture.html', id=id, tag=picture['tag'], file_name=picture['file_name'],
                        upload_date=picture['upload_date'])
        else:
            self.set_status(404)
        self.finish()


class DownHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self, id):
        image_id = ObjectId(id)
        db = client.picture_manager
        picture = db.picture.find_one({"_id": image_id})
        self.set_header('Content-Type', 'application/octet-stream')
        self.set_header('Content-Disposition', "attachment; filename=%s" % picture['file_name'])
        if picture:
            buf_size = 4096
            with open(os.path.join('', picture['file_path']), 'rb') as f:
                while True:
                    data = f.read(buf_size)
                    if not data:
                        break
                    self.write(data)
        else:
            self.set_status(404)
        self.finish()


class LoginHandler(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument('username')
        password = self.get_argument('password')
        if username == "admin":
            if password == "admin":
                self.set_secure_cookie('user', 'admin', expires_days=None)
                self.write(json_util.dumps({"message": "succ"}))
        else:
            db = client.picture_manager
            user = db.account.find_one({"username": username})
            if user and hashlib.sha1(hashlib.md5(password).hexdigest()).hexdigest() == user['password']:
                self.set_secure_cookie('user', username, expires_days=None)
                self.write(json_util.dumps({"message": "succ"}))
            else:
                self.write(json_util.dumps({"message": "用户名或密码错误,请重试！"}))

        self.finish()


class LogoutHandler(BaseHandler):
    @tornado.web.asynchronous
    def get(self):
        self.clear_cookie('user')
        self.redirect('/')


class AssignAccountHandler(BaseHandler):
    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument("username")
        password = self.get_argument("password")
        db = client.picture_manager
        inserted_id = db.account.insert_one(
            {'username': username, "password": hashlib.sha1(hashlib.md5(password).hexdigest()).hexdigest()})
        if inserted_id:
            self.write(json_util.dumps({"message": '分配成功！'}))
        else:
            self.write(json_util.dumps({"message": '分配失败！'}))

        self.finish()
