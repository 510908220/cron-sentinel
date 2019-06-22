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
    name = models.CharField(max_length=200, unique=True,
                            blank=False, null=False)

    def __str__(self):
        return self.name


class Service(BaseModel):
    class Meta:
        db_table = "service"
        unique_together = ('name', 'assigned',)
    STATUS = (
        ('ok', 'ok'),
        ('alert', 'alert'),
        ('paused', 'paused'),
        ('nodata', 'nodata'),
        ('error', 'error')
    )
    TYPES = (
        ('at', 'at'),
        ('every', 'every'),
    )

    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False, unique=True)
    assigned = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, unique=True,
                            blank=False, null=False)
    description = models.TextField(default="")
    status = models.CharField(
        choices=STATUS, default=STATUS[3][1], max_length=20)
    tp = models.CharField(choices=TYPES, default=TYPES[0][0], max_length=20)
    value = models.CharField(max_length=200, default='')

    last_check_timestamp = models.CharField(max_length=200, default='')  # 上次检查时间
    # notify
    alert_count = models.IntegerField(default=0)  # 本次已经告警的次数, 恢复后清0
    alert_interval_min = models.IntegerField(
        default=0)  # 告警间隔,比如60，意思是一小时内最多告警一次
    last_alert_timestamp = models.CharField(max_length=200, default='') # 上一次告警时间, 服务恢复后需要重置此值

    grace = models.IntegerField(default=0)
    tags = models.ManyToManyField(Tag, related_name='services')

    wechat = models.TextField(default="")
    email = models.TextField(default="")
    sms = models.TextField(default="")

    def __str__(self):
        return self.name


class Alert(BaseModel):
    class Meta:
        db_table = "alert"
        indexes = [
            models.Index(fields=['unique_id', 'created', ]),
        ]
    unique_id = models.UUIDField(
        default=uuid.uuid4, editable=False)
    service_name = models.CharField(max_length=200, default='')
    msg = models.TextField(blank=True)

    @staticmethod
    def create(unique_id, msg):
        Alert.objects.create(
            unique_id=unique_id,
            msg=msg
        )
