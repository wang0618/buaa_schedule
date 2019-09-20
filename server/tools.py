import hashlib
import logging
import re
from collections import namedtuple
from logging.handlers import RotatingFileHandler

from pyquery import PyQuery


def set_logger_to_file(logger, filename, level=logging.WARNING, propagate=False):
    """将logger配置为记录到日志"""
    ch = RotatingFileHandler(filename=filename, maxBytes=2 ** 23, encoding='utf8', backupCount=10)
    ch.setLevel(level)
    formatter = logging.Formatter('[%(asctime)s %(module)s:%(lineno)d %(funcName)s] %(message)s',
                                  datefmt='%y%m%d %H:%M:%S')
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    logger.setLevel(level)
    logger.propagate = propagate


# (0课程名称,1周次列表,2上课星期,3节次元组,4上课地点,5任课教师,6上课班号,7其他)
ScheduleItem = namedtuple('ScheduleItem', 'name weeks day time address teacher class_no desc')


def extract_schedule(raw_data):
    """从html中解析课表"""
    doc = PyQuery(raw_data)

    rows = doc('tbody>tr')
    res = []
    for row in rows.items():
        tds = list(row('td').items())
        for day, td in enumerate(tds, 8 - len(tds)):
            if day == 0:
                continue
            courses = td('div.Course-name')
            if courses:
                for item in courses.items():
                    name = item('h3').text()
                    infos = list(item('p').items())
                    credit = '学分：%s' % infos[0].text()
                    teacher_time = list(infos[1]('span').items())

                    teacher = teacher_time[0].text()
                    time_info = re.search(r'\[([0-9]+?)-([0-9]+?)周]([0-9]+?)-([0-9]+?)节', teacher_time[1].text())

                    if not time_info:
                        print(teacher_time[1].text())
                        return None

                    weeks = list(range(int(time_info.group(1)), int(time_info.group(2)) + 1))
                    time = (int(time_info.group(3)), int(time_info.group(4)))
                    address = infos[2].text()
                    # class_no = infos[3].text()

                    res.append(ScheduleItem(name, weeks, day, time, address, teacher, '', credit))
    return res


def md5(data):
    hl = hashlib.md5()
    hl.update(data.encode(encoding='utf-8'))
    return hl.hexdigest()


if __name__ == '__main__':
    data = open('../data/data.html', encoding='utf8').read()
    res = extract_schedule(data)
