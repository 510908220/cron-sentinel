import logging
from datetime import datetime

# Create your views here.
import django_filters
from django.contrib.auth.models import User
# Create your views here.
from django.shortcuts import get_object_or_404, render
from rest_framework import authentication, filters, permissions, viewsets
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from .influxdb_api import InfluxDBAPI
from .models import Service, Tag, Alert
from .serializers import ServiceSerializer, TagSerializer, AlertSerializer

from api.tasks import add_ping_async


logger = logging.getLogger('api')


def get_ping_points(params, num=10):
    results = []
    index = 1

    with InfluxDBAPI() as f:
        pings = f.get_pings(params)
    for ping in pings:
        results.append(ping)
        index += 1
        if index > num:
            break
    return results


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 25
    page_size_query_param = 'page_size'
    max_page_size = 100


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


class PingViewSet(viewsets.ViewSet):
    def list(self, request):
        unique_id = request.query_params.get('unique_id')
        count = request.query_params.get('count')
        if not count:
            count = 10
        get_object_or_404(Service, unique_id=unique_id)
        params = {
            'unique_id': unique_id
        }
        results = get_ping_points(params, int(count))

        return Response(results)

    def retrieve(self, request, pk=None):
        unique_id = pk
        value = request.query_params.get('value', '')
        if not value:
            value = 'cola'

        service_obj = get_object_or_404(Service, unique_id=unique_id)

        if service_obj.status == 'paused':
            return {
                'status': 'service is paused'
            }

        headers = request.META
        remote_addr = headers.get(
            "HTTP_X_FORWARDED_FOR", headers["REMOTE_ADDR"])
        remote_addr = remote_addr.split(",")[0]

        json_body = [
            {
                "measurement": "pings",
                "tags": {
                    "host": remote_addr,
                    "unique_id": unique_id

                },
                "time": datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
                "fields": {
                    "value": value,
                    "ua": headers.get("HTTP_USER_AGENT", "")
                }
            }
        ]
        res = add_ping_async(json_body)

        return Response({
            'status':  'ok'
        })


class ServiceViewSet(DefaultsMixin, viewsets.ModelViewSet):
    queryset = Service.objects.order_by('created')
    serializer_class = ServiceSerializer

    ordering_fields = ('updated', )
    filter_class = ServiceFilter
    filter_fields = ('tags', 'status', 'tp')

    def get_queryset(self, tags=None):
        qs = self.queryset.filter(assigned=self.request.user)
        if tags:
            values = tags.strip().split(',')
        else:
            values = []
        if not values:
            return qs

        is_tag_exist = False
        for value in values:
            tag_objs = Tag.objects.filter(name=value)
            if not tag_objs:
                continue
            is_tag_exist = True
            qs = qs.filter(tags=tag_objs[0])

        if not is_tag_exist:
            return Service.objects.none()
        return qs

    def list(self, request):
        tags = request.query_params.get('tags')
        print(tags)
        services = []
        for service in self.get_queryset(tags):
            service_dict = ServiceSerializer(service).data
            service_dict['schedule'] = '{} {}'.format(
                service_dict['tp'], service_dict['value'])

            results = get_ping_points({
                'unique_id': str(service.unique_id)
            }, 1)
            # 通知方式
            notify = []
            for notify_tp in ['email', 'wechat', 'sms']:
                if service_dict[notify_tp]:
                    notify.append(notify_tp)

            service_dict['notify'] = ' '.join(notify)
            service_dict['last_ping_time'] = results[0]['time'] if results else ''
            services.append(service_dict)
        return Response(services)

    def create(self, request):
        params = self.request.data
        logger.info('create <%s> %s', self.request.user.username, params)

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

    def destroy(self, request, pk=None):
        logger.info('delete <%s> %s', self.request.user.username, pk)
        self.get_queryset().filter(unique_id=pk).delete()
        return Response({'status': 'ok'})

    def update(self, request, pk=None):
        params = self.request.data
        logger.info('update <%s> %s %s',
                    self.request.user.username, pk, params)
        if 'tags' in params:
            tags = params.pop('tags')
            Service.objects.filter(unique_id=pk).update(**params)
            service = Service.objects.get(unique_id=pk)
            service.tags.clear()
            for tag in tags:
                tag_obj, _ = Tag.objects.get_or_create(name=tag)
                service.tags.add(tag_obj)
        else:
            Service.objects.filter(unique_id=pk).update(**params)
            service = Service.objects.get(unique_id=pk)
        service.save()  # 更新时间字段
        return Response(ServiceSerializer(service).data)


class AlertViewSet(DefaultsMixin, viewsets.ModelViewSet):
    # pagination_class = StandardResultsSetPagination
    queryset = Alert.objects.order_by('-created')
    serializer_class = AlertSerializer

    def list(self, request):
        unique_id = request.query_params.get('unique_id')
        count = int(request.query_params.get('count', 10))

        results = []
        for alert in Alert.objects.filter(unique_id=unique_id).order_by('-created')[0:count].values():
            results.append(alert)
        return Response(results)
