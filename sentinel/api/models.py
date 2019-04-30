# -*- coding:utf-8 -*-
import uuid

from django.db import models
from django.conf import settings
# Create your models here.

class BaseModel(models.Model):
    class Meta:
        abstract = True  # Set this model as Abstract
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)


class Tag(BaseModel):
    class Meta:
        db_table = "tag"
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)

    def __str__(self):
        return self.name


class Service(BaseModel):
    class Meta:
        db_table = "service"
        unique_together = ('name', 'assigned',)
    STATUS = (
        ('ok', 'ok'),
        ('alert', 'alert'),
        ('paused','paused'),
        ('nodata','nodata'),
        ('error','error') 
    )
    TYPES = (
        ('at', 'at'),
        ('every', 'every'),
    )

    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    assigned = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True, blank=False, null=False)
    status = models.CharField(choices=STATUS, default=STATUS[3][1], max_length=20)
    tp = models.CharField(choices=TYPES, default=TYPES[0][0], max_length=20)
    value = models.CharField(max_length=200, default='')

    # notify 
    alert_count = models.IntegerField(default=0)# 本次已经告警的次数, 恢复后清0
    alert_interval_min =  models.IntegerField(default=0) # 告警间隔,比如60，意思是一小时内最多告警一次
    last_alert_timestamp = models.IntegerField(default=0) # 上一次告警时间, 服务恢复后需要重置此值

    grace = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='services')

    def __str__(self):
        return self.name




class Alert(BaseModel):
    class Meta:
        db_table = "alert"
    service = models.ForeignKey(Service, related_name='pings', on_delete=models.CASCADE)
    channels = models.CharField(max_length=200, blank=True)
    msg = models.TextField(blank=True)

    def __str__(self):
        return "{}-{}".format(self.service.name, self.id)
