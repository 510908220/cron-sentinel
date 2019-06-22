from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework.exceptions import ValidationError
from .models import Tag, Service,Alert

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('id', 'name', 'created', 'updated')


class AlertSerializer(serializers.ModelSerializer):

    class Meta:
        model = Alert
        fields = ('id', 'unique_id','msg' ,'service_name','created', 'updated')


class ServiceSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)

    class Meta:
        model = Service
        fields = ('id', 'name', 'description' ,'status', 'tp', 'last_check_timestamp',
                  'value', 'grace', 'unique_id', 'alert_count', 'assigned',
                  'tags', 'alert_interval_min', 'last_alert_timestamp','email', 'wechat', 'sms',
                  'created', 'updated')
    assigned = serializers.SlugRelatedField(
        slug_field=User.USERNAME_FIELD,
        required=False,
        allow_null=True,
        queryset=User.objects.all()
    )

    def get_links(self, obj):
        request = self.context['request']
        links = {
            'self': reverse('service-detail', kwargs={'pk': obj.pk}, request=request),
            'assigned': None
        }
        if obj.assigned:
            links['assigned'] = reverse(
                'user-detail', kwargs={User.USERNAME_FIELD: obj.assigned}, request=request)
        return links

    def validate(self, attrs):
        return attrs


class UserSerializer(serializers.ModelSerializer):
    full_name = serializers.CharField(source='get_full_name', read_only=True)
    links = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', User.USERNAME_FIELD, 'password',
                  'full_name', 'is_superuser', 'links')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User(
            username=validated_data['username']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

    def get_links(self, obj):
        request = self.context['request']
        return {
            'self': reverse('user-detail', kwargs={User.USERNAME_FIELD: obj.get_username()}, request=request)
        }
