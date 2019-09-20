import logging
import os

import tornado.web
from tornado.log import access_log, app_log, gen_log
from tornado.options import define, options

from server.class_calander import ClassTime
from server.handlers import handlers
from server.setting import project_dir, term_start_date
from server.tools import set_logger_to_file

define("port", default=5000, help="run on the given port", type=int)
dev = bool(os.environ.get('DEV'))

if __name__ == "__main__":
    tornado.options.parse_command_line()

    ClassTime.set_startday(term_start_date.year, term_start_date.month, term_start_date.day)

    if not dev:
        # 线上环境配置
        access_log.disabled = True
        log_file = '%s/../app-%s.log' % (project_dir, options.port)
        set_logger_to_file(app_log, filename=log_file)
        set_logger_to_file(gen_log, filename=log_file)
    else:
        access_log.setLevel(logging.DEBUG)
        app_log.setLevel(logging.DEBUG)
        gen_log.setLevel(logging.DEBUG)
        logging.info('Dev environment')

    app = tornado.web.Application(handlers=handlers, debug=dev)
    http_server = tornado.httpserver.HTTPServer(app, xheaders=True)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
