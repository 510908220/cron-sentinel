# -*- encoding: utf-8 -*-

'''
定义需要后台运行的任务
'''

from huey import crontab
from huey.contrib.djhuey import task, periodic_task, db_task

from api.influxdb_api import InfluxDBAPI


@task()
def add_ping_async(json_body):
    with InfluxDBAPI() as f:
        status = f.write_pings(json_body)
    return status
