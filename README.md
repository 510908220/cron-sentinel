# cron-sentinel
is  a tool to monitor your scheduled jobs (or cron jobs). 

## influxdb

> 因为在阿里云环境,有防火墙, 所以没开启http认证


```
influx -precision rfc3339
```

创建数据库
```
CREATE DATABASE pings
```

查看保留策略
```
show retention policies on pings
```

创建一个`30`天的策略
```
 create retention policy "30_days" on "pings" duration 30d replication 1 default
```
## MYSQL

```
docker run -p 3066:3306 --name mysql -v $PWD/conf:/etc/mysql/conf.d -v $PWD/logs:/logs -v $PWD/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD='!@#$ESZAQ' -d mysql
```

创建数据库

```
CREATE DATABASE sentinel  CHARACTER SET utf8 COLLATE utf8_general_ci;
```
