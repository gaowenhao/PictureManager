# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description:
                用于对项目进行一些全局的配置
"""
import os
import motor.motor_tornado

PORT = 8888

# FILE_UPLOAD_PATH = '/home/vincent/UploadFile'
FILE_UPLOAD_PATH = 'D://UploadFile'
PREVIEW_FILE_POSTFIX = '_pre'
EACH_PAGE_ITEM = 24

client = motor.motor_tornado.MotorClient()
db = client['picture_manager']

APP_SETTING = {
    'debug': True,
    "autoreload": True,
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    # "xsrf_cookies": True,
    'cookie_secret': 'HUAYI_T39Z012KZU93',
    'db': db
}
