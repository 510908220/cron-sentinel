# -*- encoding: utf-8 -*-

'''
python操作influxdb相关接口封装

https://influxdb-python.readthedocs.io/en/latest/resultset.html

'''

from django.conf import settings

from influxdb import InfluxDBClient


class InfluxDBAPI(object):
    def __init__(self):
        self.client = InfluxDBClient(**settings.INFLUXDB)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.client.close()

    def write_pings(self, json_body):
        '''
        json_body = [
            {
                "measurement": "pings",
                "tags": {
                    "host": "10.5.2.5",
                    "service_unique_id": 'xxxxxxx'
                },
                "time": "2019-6-4 12:54:39",
                "fields": {
                    "value": 0.8
                }
            }
        ]
        '''
        return self.client.write_points(json_body)

    def get_pings(self, tags):
        rs = self.client.query('select * from pings ORDER by time DESC;')
        # 暂时这里都是pings
        ping_points = rs.get_points(measurement='pings', tags=tags)
        for ping_point in ping_points:
            yield ping_point
