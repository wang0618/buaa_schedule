import json
import os
from tempfile import NamedTemporaryFile
from concurrent.futures import ThreadPoolExecutor
from qiniu import Auth, put_data
from tornado.web import RequestHandler
from tornado.web import StaticFileHandler
from tornado.ioloop import IOLoop
from server.class_calander import CalUtil
from server.setting import project_dir
from server.setting import qiniu_access_key, qiniu_bucket_name, qiniu_secret_key
from server.tools import extract_schedule, md5


class ICSHandler(RequestHandler):
    executor = ThreadPoolExecutor(max_workers=8)

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

    async def post(self):
        raw_data = self.get_body_argument('data')
        try:
            alarm_minute = int(self.get_body_argument('alarm_minute', 15))
        except ValueError:
            alarm_minute = 15
        try:
            trans = json.loads(self.get_body_argument('trans', '{}'))
        except:
            trans = {}

        try:
            schedules = extract_schedule(raw_data)
        except:
            # 记录出错数据
            open('%s/../error_data/%s.html' % (project_dir, md5(raw_data)), 'w', encoding='utf8').write(raw_data)
            raise

        # 更新上课地点
        new_schedules = list(map(lambda i: i._replace(address=trans.get(i.name, i.address)), schedules))

        apple_cal = CalUtil.get_calander(new_schedules, alarm_minute=alarm_minute,
                                         use_recurrence=True)  # ios平台开启提醒和循环事件
        cal = CalUtil.get_calander(new_schedules, alarm_minute=None)  # outlook不支持提醒设置

        # CalUtil.save_cal('out.ics', cal)

        key = md5(raw_data)
        # 将课表文件异步保存到七牛云上
        await IOLoop.current().run_in_executor(self.executor, self.save_to_qiniu, key, cal.to_ical(), apple_cal.to_ical())

        self.succeed(key)

    async def save_to_qiniu(self, key, data, app_data):
        q = Auth(qiniu_access_key, qiniu_secret_key)
        filename = '%s.ics' % key
        token = q.upload_token(qiniu_bucket_name, filename, 3600 * 24 * 200)
        put_data(token, filename, data, mime_type='text/calendar')

        filename = '%s_apple.ics' % key
        token = q.upload_token(qiniu_bucket_name, filename, 3600 * 24 * 200)
        put_data(token, filename, app_data, mime_type='text/calendar')

    def succeed(self, data=''):
        self.write(json.dumps({'data': data, 'status': True}))

    def error(self, msg=''):
        self.write(json.dumps({'status': False, 'message': msg}))


handlers = [
    (r"/api/ics", ICSHandler),
    (r"/(.*)", StaticFileHandler, {"path": '%s/../html_root' % project_dir, 'default_filename': 'index.html'}),
]
