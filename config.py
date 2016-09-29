# encoding=utf-8
"""
    @author: gaowenhao
    @email: vevz@163.com
    @description:
                用于对项目进行一些全局的配置
"""
import os

PORT = 8000

FILE_UPLOAD_PATH = '/home/vincent/UploadFile'

APP_SETTING = {
    'debug': True,
    'static_path': os.path.join(os.path.dirname(__file__), 'static'),
    'template_path': os.path.join(os.path.dirname(__file__), 'template'),
    "xsrf_cookies": True,
    'cookie_secret': 'The Art Affect The Word.'
}
