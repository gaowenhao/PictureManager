# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description:  实现主要的功能
"""
import tornado.web
import os
import config


class IndexHandelr(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')


class UploadHandler(tornado.web.RequestHandler):
    def get(self):
        return self.render('upload.html')

    def post(self):
        file_metas = self.request.files['files']
        for file_meta in file_metas:
            file_path = os.path.join(config.FILE_UPLOAD_PATH, file_meta['filename'])
            with open(file_path, 'wb') as up:
                up.write(file_meta['body'])
