# -*- encoding: utf-8 -*-

'''
定义需要后台运行的任务
'''

import time
import datetime
from huey import crontab
from huey.contrib.djhuey import task, periodic_task, db_task
from api.influxdb_api import InfluxDBAPI
from api.models import Service


def get_last_ping(unique_id):
    '''
    TODO:后续慢的话加缓存
    '''
    sql = "select last(value) as value,time  from pings where unique_id = '{}';".format(
        unique_id)
    with InfluxDBAPI() as f:
        pings = f.query_pings(sql)

    for ping in pings:
        return ping


@task()
def update_service_status(ping):
    value = ping['fields']['value']
    unique_id = ping['tags']['unique_id']
    last_ping = get_last_ping(unique_id)
    s = Service.objects.get(unique_id=unique_id)
    alert_count = s.alert_count

    if not last_ping:
        print('first:', status)
        # 第一次
        if value == 'cola':
            status = 'ok'
        else:
            status = 'error'
    else:
        print('multi:', value)
        if s.status in ['alert', 'nodata']:
            print('long-->ok')
            # 从长时间未ping--->恢复过来了
            if value == 'cola':  # 近两次都是正常
                status = 'ok'
                alert_count = 0
            else:
                status = 'error'  # ok--->error
                alert_count += 1
            print('--->', status)
        elif last_ping['value'] == 'cola':
            if value == 'cola':  # 近两次都是正常
                status = 'ok'
            else:
                status = 'error'  # ok--->error
                alert_count += 1
            print('ok-->', status)
        else:
            if value == 'cola':  # error--> ok
                pass
            else:   # error--->error,频率限制
                alert_count += 1
            print('error-->', status)

    s.status = status
    s.alert_count = alert_count
    s.last_check_timestamp = time.mktime(datetime.datetime.strptime(
        ping['time'], "%Y-%m-%dT%H:%M:%SZ").timetuple())

    s.save(update_fields=['last_check_timestamp', 'status', 'alert_count'])


@task()
def add_ping_async(ping_list):
    with InfluxDBAPI() as f:
        status = f.write_pings(ping_list)
    update_service_status(ping_list[0])
    return ping_list[0]


# @task()
# def alert(json_body):
#     with InfluxDBAPI() as f:
#         status = f.write_pings(json_body)
#     return status


# @task()
# def notify(json_body):
#     with InfluxDBAPI() as f:
#         status = f.write_pings(json_body)
#     return status


@periodic_task(crontab(minute='*/5'))
def every_five_mins():
    # This is a periodic task that executes queries.
    # 如果任务长时间没有ping，状态置位alert
    print('This is a periodic task that executes queries')
