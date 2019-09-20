#!/usr/bin/env python
# coding=utf-8

import logging
from datetime import datetime, date, timedelta

import pytz
from icalendar import Calendar, Event, vDatetime


class ClassTime:
    tzinfo = pytz.timezone('Asia/Shanghai')
    start_day = None  # 第一周的周一

    day_time = [(480, 525),
                (530, 575),
                (590, 635),
                (640, 685),
                (690, 735),
                (840, 885),
                (890, 935),
                (950, 995),
                (1000, 1045),
                (1050, 1095),
                (1140, 1185),
                (1190, 1235),
                (1240, 1285),
                (1290, 1335)]  # (开始分钟数，结束分钟数)

    @classmethod
    def set_startday_from_currentweek(cls, week):
        assert week > 0
        t = date.today()
        datetime.now(cls.tzinfo)
        # datetime.now()
        start_day = t - timedelta(days=t.weekday(), weeks=(week - 1))
        cls.start_day = datetime(start_day.year, start_day.month, start_day.day, tzinfo=cls.tzinfo)
        # cls.start_day = datetime(start_day.year, start_day.month, start_day.day)

    @classmethod
    def set_startday(cls, year, month, day):
        # cls.start_day = datetime(year, month, day)
        cls.start_day = datetime(year, month, day, tzinfo=cls.tzinfo)

    @classmethod
    def get_class_time(cls, week, day, num, start=True):
        """
        获取课程时间
        :param day_time: 每天作息时间
        :param week: int 周数
        :param day: int 星期数ISO
        :param num: int 节数
        :param start: bool 是否获取开始时间
        :return: 开始时间
        """
        assert cls.start_day, "未设置学期开始时间"
        assert week > 0 and day > 0 and num <= len(cls.day_time), "课程节数有误: week:%s day:%s num:%s" % (week, day, num)
        t = cls.start_day + timedelta(days=(day - 1), weeks=(week - 1),
                                      minutes=cls.day_time[num - 1][0 if start else 1])
        return t


class CalUtil:
    @staticmethod
    def __get_rdate(weeks, day, nums):
        res = []
        for week in weeks:
            try:
                t = ClassTime.get_class_time(week, day, nums[0])
            except AssertionError as e:
                logging.error('get a error in classtime:' + str(e))
                continue
            res.append(vDatetime(t).to_ical())
        return ','.join(res)

    @classmethod
    def __get_recurrence_event(cls, c):
        # (0课程名称,1周次列表,2上课星期,3节次元组,4上课地点,5任课教师,6上课班号,7其他)
        event = Event()
        event.add('summary', c[0])  # title
        event.add('dtstart', ClassTime.get_class_time(c[1][0], c[2], c[3][0]))
        event.add('dtend', ClassTime.get_class_time(c[1][0], c[2], c[3][1], False))
        event.add('DESCRIPTION', '任课教师:%s\n上课班号:%s\n%s' % (c[5], c[6], c[7]))
        event.add('location', c[4])
        event['RDATE;TZID=Asia/Shanghai'] = cls.__get_rdate(c[1], c[2], c[3])
        # event['rrule'] = vText('FREQ=WEEKLY;COUNT=5;INTERVAL=2')
        return event

    @classmethod
    def __get_events(cls, c):
        # (0课程名称,1周次列表,2上课星期,3节次元组,4上课地点,5任课教师,6上课班号,7其他)
        for week in c[1]:
            event = Event()
            event.add('summary', c[0])  # title
            event.add('uid', '%s_%s_%s-%s' % (week, c[2], c[3][0], c[3][1]))  # uid
            try:
                event.add('dtstart', ClassTime.get_class_time(week, c[2], c[3][0]))
                event.add('dtend', ClassTime.get_class_time(week, c[2], c[3][1], False))
            except AssertionError as e:
                logging.error('get a error in classtime:' + str(e))
                continue
            event.add('DESCRIPTION', '任课教师:%s\n上课班号:%s\n%s' % (c[5], c[6], c[7]))
            event.add('location', c[4])
            yield event

    @classmethod
    def get_calander(cls, classtables, use_recurrence=False):
        """
        :param classtables: [(0课程名称,1周次列表,2上课星期,3节次元组,4上课地点,5任课教师,6上课班号,7其他),..]
        :param use_recurrence: 是否使用 循环事件 生成ics, 某些日历软件可能无法识别使用 循环事件 生成的ics
        :return:
        """
        cal = Calendar()
        cal.add('prodid', '-//buaa classtable//wecqu.com//')
        cal.add('version', '2.0')
        cal.add('X-WR-CALNAME', '课表')
        cal.add('TZID', 'Asia/Shanghai')

        for i in classtables:
            if use_recurrence:
                cal.add_component(cls.__get_recurrence_event(i))
            else:
                try:
                    for event in cls.__get_events(i):
                        cal.add_component(event)
                except Exception as e:
                    raise
                    logging.error('Got Exception:' + str(e))
        return cal

    @staticmethod
    def save_cal(path, cal):
        f = open(path, 'wb')
        f.write(cal.to_ical())
        f.close()


"""
ClassTime.set_startday(2017,9,4)
cal = CalUtil.get_calander(classtables, False)
CalUtil.save_cal(os.path.join('.', 'example_nr.ics'), cal)
"""

if __name__ == '__main__':
    from tools import extract_schedule

    data = open('../data/data.html', encoding='utf8').read()
    res = extract_schedule(data)
