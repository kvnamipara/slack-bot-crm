# -*- coding: utf-8 -*-
from apscheduler.schedulers.blocking import BlockingScheduler
from schedule import check_for_midnight

sched = BlockingScheduler()


@sched.scheduled_job('cron',minute='0,15,30,45')
def scheduled_job():
    check_for_midnight()

sched.start()
