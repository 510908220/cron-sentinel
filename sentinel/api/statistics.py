# -*- encoding: utf-8 -*-

'''
统计数据
'''

import json
from datetime import datetime, timedelta

from django.db.models import Count

from api.models import Alert, Service

from .influxdb_api import InfluxDBAPI


def get_service_run(unique_id):
    '''
    获取服务近一月的ping次数
    '''
    sql = "SELECT count(value) FROM  pings WHERE time > now() - 30d and unique_id = {} GROUP BY time(1d)".format(unique_id)

    labels = []
    data = []
    with InfluxDBAPI() as f:
        pings = f.query_pings(sql)

    for ping in pings:
        labels.append(ping['time'])
        data.append(ping['count'])
    return {
        'labels': labels,
        'data': data
    }


def get_dashboard(user):
    # 1. 服务数统计
    service_dict = {
        'total': 0,
        'ok': 0,
        'bad': 0
    }
    for item in Service.objects.filter(assigned=user).values('status').annotate(total=Count('status')):
        service_dict['total'] += item['total']
        if item['status'] == 'ok':
            service_dict['ok'] += 1
        else:
            service_dict['bad'] += 1

    # 2. 告警信息统计
    unique_ids = [s['unique_id']
                  for s in Service.objects.filter(assigned=user).values('unique_id')]
    alert_count = Alert.objects.filter(unique_id__in=unique_ids).count()

    last_month = datetime.utcnow() - timedelta(days=30)
    queryset = Alert.objects.filter(unique_id__in=unique_ids, created__gt=last_month).extra(
        select={'day': 'date(created)'}).values('day').annotate(sum=Count('id'))

    alert_dict = {
        'labels': [],
        'data': [],
        'count': alert_count
    }
    for item in queryset:
        alert_dict['labels'].append(item['day'].strftime("%Y-%m-%d"))
        alert_dict['data'].append(int(item['sum']))
    return {
        'service': service_dict,
        'alert': alert_dict
    }
