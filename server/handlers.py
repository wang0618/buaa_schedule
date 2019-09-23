import json
import os
from tempfile import NamedTemporaryFile

from qiniu import Auth, put_data
from tornado.gen import coroutine
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler

from server.class_calander import CalUtil
from server.setting import project_dir
from server.setting import qiniu_access_key, qiniu_bucket_name, qiniu_secret_key
from server.tools import extract_schedule, md5


class ICSHandler(RequestHandler):

    def set_default_headers(self):
        if self.request.headers.get('origin', '').startswith('https://gsmis.e.buaa.edu.cn'):
            self.set_header("Access-Control-Allow-Origin", "https://gsmis.e.buaa.edu.cn")
        else:
            self.set_header("Access-Control-Allow-Origin", "http://gsmis.buaa.edu.cn")

        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Content-Type', 'application/json')

    def write_error(self, status_code, **kargs):
        self.set_status(200)
        self.error('请求出错, 您可以向开发者反馈此问题')

    @coroutine
    def post(self):
        raw_data = self.get_body_argument('data')
        alarm_minute = int(self.get_body_argument('alarm_minute', 15))

        try:
            schedules = extract_schedule(raw_data)
        except:
            open('%s/../error_data/%s.ics' % (project_dir, md5(raw_data)), 'w', encoding='utf8').write(raw_data)
            raise
        apple_cal = CalUtil.get_calander(schedules, alarm_minute=alarm_minute, use_recurrence=True)  # ios平台开启提醒和循环事件
        cal = CalUtil.get_calander(schedules, alarm_minute=None)  # outlook不支持提醒设置

        # CalUtil.save_cal('out.ics', cal)

        # 保存到七牛云上
        q = Auth(qiniu_access_key, qiniu_secret_key)
        key = md5(raw_data)
        filename = '%s.ics' % key
        token = q.upload_token(qiniu_bucket_name, filename, 3600 * 24 * 200)
        put_data(token, filename, cal.to_ical(), mime_type='text/calendar')

        filename = '%s_apple.ics' % key
        token = q.upload_token(qiniu_bucket_name, filename, 3600 * 24 * 200)
        put_data(token, filename, apple_cal.to_ical(), mime_type='text/calendar')

        self.succeed(key)

    def succeed(self, data=''):
        self.write(json.dumps({'data': data, 'status': True}))

    def error(self, msg=''):
        self.write(json.dumps({'status': False, 'message': msg}))


handlers = [
    (r"/api/ics", ICSHandler),
    (r"/(.*)", StaticFileHandler, {"path": '%s/../html_root' % project_dir, 'default_filename': 'index.html'}),
]
