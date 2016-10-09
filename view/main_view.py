# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description:  实现主要的功能
"""
from pymongo import MongoClient
from bson import ObjectId, json_util
import shutil
import tornado.escape
import tornado.web
import config
import os
import datetime
import uuid

client = MongoClient('mongodb://localhost:27017/')  # 创建连接


class IndexHandelr(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class UploadHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render('upload.html')

    def data_received(self, chunk):
        pass

    # 处理文件上传
    @tornado.web.asynchronous
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
        elif length_kb < 10240:
            return str(length_kb / 1024) + "MB"
        elif length_kb < 102400:
            return str(length_kb / (1024 * 1024)) + "GB"


class SearchHandler(tornado.web.RequestHandler):
    def get(self):
        db = client.picture_manager
        search_keys = self.get_argument("search_keys").split(" ")
        if len(search_keys) < 1:
            self.write("错误,关键字不能为空.")

        page = self.get_argument('page', 1)
        query_post = {
            "$and": [{"upload_date": {"$gt": "2016-10-01"}}, {"upload_date": {"$lt": "2016-11-01"}},
                     {"$or": [
                         # {"file_name": {"$regex": 'a', "$options": "i"}}
                     ]}
                     ]
        }

        for search_key in search_keys:
            query_post['$and'][2]['$or'].append({"file_name": {"$regex": search_key, "$options": "i"}})
            query_post['$and'][2]['$or'].append({"tag": {"$regex": search_key, "$options": "i"}})

        result = db.picture.find(query_post)

        self.write(json_util.dumps(result))


class ImageHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, id):
        image_id = ObjectId(id)
        db = client.picture_manager
        picture = db.picture.find_one({"_id": image_id})
        self.set_header("content-type", "image/jpg")
        self.write(open(picture['preview_file_path'], "rb").read())
        self.finish()
