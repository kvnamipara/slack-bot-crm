# -*- coding: utf-8 -*-
import os
from apscheduler.schedulers.blocking import BlockingScheduler
from schedule import check_for_midnight,send_test_message

sched = BlockingScheduler()

@sched.scheduled_job('interval', seconds=20)
def timed_job():
    send_test_message()

@sched.scheduled_job('cron',minute='0,15,30,45')
def scheduled_job():
    check_for_midnight()

sched.start()