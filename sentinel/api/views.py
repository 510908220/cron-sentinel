from django.shortcuts import render
from datetime import datetime
# Create your views here.
from django.shortcuts import render
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

# Create your views here.
import django_filters
from rest_framework import (authentication,
                            filters,
                            permissions,
                            viewsets)


from .models import Tag, Service
from .serializers import TagSerializer, ServiceSerializer

from .influxdb_api import InfluxDBAPI
from django.contrib.auth.models import User


class DefaultsMixin(object):
    authentication_classes = (
        authentication.BasicAuthentication,
        authentication.TokenAuthentication
    )
    permission_classes = (
        permissions.IsAuthenticated,
    )

    filter_backends = (
        django_filters.rest_framework.DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter
    )


class M2MFilter(django_filters.Filter):

    def filter(self, qs, value):
        if not value:
            return qs

        values = value.strip().split(',')
        for v in values:
            tag_objs = Tag.objects.filter(name=v)
            if not tag_objs:
                continue
            qs = qs.filter(tags=tag_objs[0])
        return qs


class ServiceFilter(django_filters.FilterSet):
    tags = M2MFilter(field_name='tags')

    class Meta:
        model = Service
        fields = ('tags',)


class TagViewSet(DefaultsMixin, viewsets.ModelViewSet):
    queryset = Tag.objects.order_by('created')
    serializer_class = TagSerializer
    ordering_fields = ('created', )

    def get_queryset(self):
        return self.queryset.all()


class PingViewSet(DefaultsMixin, viewsets.ViewSet):

    def list(self, request):
        service_unique_id = request.query_params.get('service_unique_id')
        params = {
            'username': self.request.user.username
        }
        if service_unique_id:
            params.update({
                'service_unique_id': service_unique_id
            })
        results = []
        index = 1
        with InfluxDBAPI() as f:
            pings = f.get_pings(params)
        for ping in pings:
            results.append(ping)
            index += 1
            if index > 10:
                break

        return Response(results)

    def create(self, request):
        service_unique_id = request.data.get('service_unique_id')
        value = request.data.get('value')

        service_obj = get_object_or_404(Service, unique_id=service_unique_id)

        headers = request.META
        remote_addr = headers.get(
            "HTTP_X_FORWARDED_FOR", headers["REMOTE_ADDR"])
        remote_addr = remote_addr.split(",")[0]

        json_body = [
            {
                "measurement": "pings",
                "tags": {
                    "username": self.request.user.username,
                    "host": remote_addr,
                    "service_unique_id": service_unique_id,
                    "ua": headers.get("HTTP_USER_AGENT", ""),

                },
                "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "value": value
                }
            }
        ]

        status = True
        with InfluxDBAPI() as f:
            status = f.write_pings(json_body)

        return Response({
            'status': status
        })


class ServiceViewSet(DefaultsMixin, viewsets.ModelViewSet):
    queryset = Service.objects.order_by('created')
    serializer_class = ServiceSerializer

    ordering_fields = ('updated', )
    filter_class = ServiceFilter
    filter_fields = ('tags', 'status', 'tp')

    def get_queryset(self):
        return self.queryset.all()

    def list(self, request):
        services = []
        for service in self.get_queryset():
            service_dict = ServiceSerializer(service).data
            service_dict['schedule'] = '{} {}'.format(
                service_dict['tp'], service_dict['value'])
            services.append(service_dict)
        return Response(services)

    def create(self, request):
        params = self.request.data
        tags = params.pop('tags', '')

        params['assigned'] = request.user

        service = Service(**params)
        service.save()
        for tag in tags.strip().split(","):
            if not tag:
                continue
            tag_obj, _ = Tag.objects.get_or_create(name=tag)
            service.tags.add(tag_obj)

        return Response(ServiceSerializer(service).data)

    def update(self, request, pk=None):
        params = self.request.data

        if 'tags' in params:
            tags = params.pop('tags')
            Service.objects.filter(pk=pk).update(**params)
            service = Service.objects.get(id=pk)
            service.tags.clear()
            for tag in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                service.tags.add(tag_obj)
        else:
            Service.objects.filter(pk=pk).update(**params)
            service = Service.objects.get(id=pk)
        service.save()  # 更新时间字段
        return Response(ServiceSerializer(service).data)
