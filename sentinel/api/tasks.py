# -*- encoding: utf-8 -*-

'''
定义需要后台运行的任务
'''

import time
import datetime
from huey import crontab
from huey.contrib.djhuey import task, periodic_task, db_task
from api.influxdb_api import InfluxDBAPI
from api.models import Service, Alert
from api import notice
import logging

logger = logging.getLogger('huey')


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
    recover = False
    if not last_ping:
        logger.info('first:%s', status)
        # 第一次
        if value == 'cola':
            status = 'ok'
        else:
            status = 'error'
    else:
        logger.info('multi:%s', value)
        if s.status in ['alert', 'nodata']:
            logger.info('long-->ok')
            # 从长时间未ping--->恢复过来了
            if value == 'cola':  # 近两次都是正常
                status = 'ok'
                recover = True
            else:
                status = 'error'  # ok--->error
            logger.info('--->%s', status)
        
        elif s.status in ['error']:
            if value == 'cola':  # error-->ok
                status = 'ok'
                recover = True
            else:
                status = 'error'

        else:
            if value == 'cola':  # ok-->ok
                status = 'ok'
            else:
                status = 'error' # ok---error


    s.status = status
    s.last_check_timestamp = ping['time']

    s.save(update_fields=['last_check_timestamp', 'status', 'alert_count'])

    if status == 'error':
        notify(unique_id, 'error', 'has error:{}'.format(value))
    elif  status == 'ok' and recover:
        notify(unique_id, 'ok', 'recover')


@task()
def add_ping_async(ping_list):
    with InfluxDBAPI() as f:
        status = f.write_pings(ping_list)
    update_service_status(ping_list[0])
    return ping_list[0]


@task()
def alert(json_body):
    with InfluxDBAPI() as f:
        status = f.write_pings(json_body)
    return status


def notify(unique_id, status, msg):
    service = Service.objects.get(unique_id=unique_id)
    logger.info('begin notify service:%s', service.name)
    # 1. change service status
    service.status = status
    # 2. Create alert
    Alert.objects.create(
        unique_id=service.unique_id,
        service_name=service.name,
        msg='{} {}'.format(service.name, msg)
    )

    if s.last_alert_timestamp:
        period = pendulum.now(tz='UTC') - \
            pendulum.parse(s.last_alert_timestamp)
        if period.total_minutes() <= service.alert_interval_min:
            logger.info('end notify service:%s, %s min shoule only one alert',
                        service.name, service.alert_interval_min)
            return
    # 3. notify
    level = {
        'alert': 'warning',
        'error': 'danger',
        'ok': 'primary'
    }.get(status)
    params = {
        'name': service.name,
        'status': status,
        'level': level,
        'title': '{} {}'.format(service.name, msg),
        'msg': '{} {}'.format(service.name, msg)
    }
    notice.alert({
        'wechat': service.wechat,
        'email': service.email,
        'sms': service.sms
    }, params)

    s.last_alert_timestamp = pendulum.now(tz='UTC').to_datetime_string()
    s.save(update_fields=['status', 'last_alert_timestamp'])
    logger.info('end notify service:%s', service.name)


def process_at_service(service):
    """
    当 当前时间 > at时,看[at, at + grace]之间是否有上报的数据
    """
    at = pendulum.parse(
        service.value, tz=settings.TIME_ZONE).in_timezone('UTC')
    last_created = pendulum.parse(service.last_check_timestamp)
    now = pendulum.now(tz='UTC')

    if now < at.add(minutes=int(service.grace)):
        return
    if last_created < at:
        notify(service.unique_id, 'alert', 'at no ping')


def process_every_service(service):
    """
    当前时间距离上一次上报时间 > value + grace就告警
    """
    now = pendulum.now(tz='UTC')
    period = now - pendulum.parse(service.last_check_timestamp)
    if period.total_minutes() > (int(service.value) + int(service.grace)):
        notify(service.unique_id, 'alert', 'every no ping')


@periodic_task(crontab(minute='*/5'))
def every_five_mins():
    # This is a periodic task that executes queries.
    # 如果任务长时间没有ping，状态置位alert
    timestamp = time.time()
    for service in Service.objects.all():
        if not service.last_check_timestamp:
            continue
        if service.tp = 'at':
            process_at_service(service)
        elif service.tp = 'every':
            process_every_service(service)
