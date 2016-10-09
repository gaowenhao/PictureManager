# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description: 
"""
import tornado.web
from tornado.web import url as url
import config
from view import main_view as mv  # 主控制器简写


def build_application():
    return tornado.web.Application([
        url(r'/', mv.IndexHandelr),
        url(r'/upload', mv.UploadHandler),
        url(r'/search', mv.SearchHandler),
        url(r'/image/(.+)', mv.ImageHandler),
    ], **config.APP_SETTING)


if __name__ == "__main__":
    application = build_application()
    application.listen(config.PORT)
    tornado.ioloop.IOLoop.current().start()
