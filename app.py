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
        url(r'/', mv.IndexHandelr),  # 主页
        url(r'/upload', mv.UploadHandler),  # 文件上传
        url(r'/search', mv.SearchHandler),  # 文件搜索
        url(r'/image/(.+)', mv.ImageHandler),  # 图片预览获取
        url(r'/picture/(.+)', mv.PictureHandler),  # 图片详细信息获取
        url(r'/download/(.+)', mv.DownHandler),  # 图片下载
        url(r'/login', mv.LoginHandler),  # 登录
        url(r'/logout', mv.LogoutHandler),  # 登出
        url(r'/assign_account', mv.AssignAccountHandler),  # 登出
    ], **config.APP_SETTING)


if __name__ == "__main__":
    application = build_application()
    application.listen(config.PORT, max_body_size=5 * 1024 * 1024 * 1024)  # 最大限制为5GB  ，也就是一次上传文件最好不超过5GB
    tornado.ioloop.IOLoop.current().start()
