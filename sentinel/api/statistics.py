# -*- encoding: utf-8 -*-

'''
统计数据
'''

import json
from .influxdb_api import InfluxDBAPI


def get_service_run(unique_id):
    '''
    获取服务近一月的ping次数
    '''
    sql = "SELECT count(value) FROM  pings WHERE time > now() - 7d GROUP BY time(1d)"

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
