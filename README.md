# cron-sentinel
is  a tool to monitor your scheduled jobs (or cron jobs). 

## influxdb

#### 数据库创建
> 因为在阿里云环境,有防火墙, 所以没开启http认证


```
influx -precision rfc3339
```

创建数据库
```
CREATE DATABASE sentinel
```

查看保留策略
```
show retention policies on sentinel
```

创建一个`30`天的策略
```
 create retention policy "30_days" on "sentinel" duration 30d replication 1 default
```

#### python操作

https://github.com/influxdata/influxdb-python
https://influxdb-python.readthedocs.io/en/latest/resultset.html

```python
from influxdb import InfluxDBClient
client = InfluxDBClient('localhost', 8086, 'root', 'root', 'sentinel')
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
client.write_points(json_body)

result = client.query('select value from pings;')

print("Result: {0}".format(result))

```

## MYSQL

```shell
docker run -p 3066:3306 --name mysql -v $PWD/conf:/etc/mysql/conf.d -v $PWD/logs:/logs -v $PWD/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD='!@#$ESZAQ' -d mysql
```

创建数据库

```sql
CREATE DATABASE sentinel  CHARACTER SET utf8 COLLATE utf8_general_ci;
```

## 接口

#### 获取服务对应的上报数据

```
/api/pings/?service_unique_id=d4494a5b-b6e6-4654-b19c-aae65642aa84
```

#### 获取当前登陆用户的服务

```
/api/services/?tags=aaa
```


## 消息队列

#### redis安装
```
docker run --name  sentinel-redis -v  /opt/redis_data:/data  -d redis
```

https://github.com/coleifer/huey

## 通知

1. NODATA   ---->   OK 启动
2. OK----------> DOWN 异常
3. DOWN--------ok 恢复


## 部署

- redis
- consumer
- nginx :
    - uwsgi
    - uwsgi