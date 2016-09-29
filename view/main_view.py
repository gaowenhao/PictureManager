# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description:  实现主要的功能
"""
import tornado.web


class IndexHandelr(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.render('index.html')
