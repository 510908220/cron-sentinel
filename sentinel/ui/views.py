# -*- encoding: utf-8 -*-


from django.shortcuts import render

# Create your views here.

import os
import json
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.generic.base import TemplateView
from django.contrib.auth import logout
from rest_framework.authtoken.models import Token
from api.models import Service
from django.shortcuts import get_object_or_404
from api.statistics import get_service_run


def get_user_token(user):
    token = Token.objects.get(user=user)
    return token.key


def logout_user(request):
    logout(request)
    return render(request, "registration/login.html")


def login_user(request):
    logout(request)
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect('/')
    return render(request, "registration/login.html")


class DashboardView(TemplateView):
    template_name = "dashboard.html"

    def get_context_data(self, **kwargs):
        context = super(DashboardView, self).get_context_data(**kwargs)
        context['title'] = ""
        print(self.request.user, type(self.request.user))
        context['token'] = get_user_token(self.request.user)
        return context


class ServiceItemView(TemplateView):
    template_name = "service/item.html"

    def get_context_data(self, **kwargs):
        service_obj = get_object_or_404(Service, unique_id=kwargs['id'])
        context = super(ServiceItemView, self).get_context_data(**kwargs)
        context['title'] = service_obj.name
        context['description'] = service_obj.description
        context['unique_id'] = kwargs['id']
        # https://cronhub.io/ping/9cb771e0-5f5e-11e9-877e-b9a45e5b7fc2

        context['url'] = 'http://{ip}/api/pings/{unique_id}/?value='.format(
            ip=settings.SERVER_IP,
            unique_id=kwargs['id']
        )

        context['chart'] = get_service_run(kwargs['id'])
        print(context['chart'])
        context['token'] = get_user_token(self.request.user)
        return context


class ServiceView(TemplateView):
    template_name = "service/main.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceView, self).get_context_data(**kwargs)
        context['title'] = "service"
        context['token'] = get_user_token(self.request.user)
        return context


class PingView(TemplateView):
    template_name = "service/ping.html"

    def get_context_data(self, **kwargs):
        context = super(PingView, self).get_context_data(**kwargs)
        context['title'] = "ping"
        context['token'] = get_user_token(self.request.user)
        return context


class AlertView(TemplateView):
    template_name = "service/alert.html"

    def get_context_data(self, **kwargs):
        context = super(AlertView, self).get_context_data(**kwargs)
        context['title'] = "alert"
        context['token'] = get_user_token(self.request.user)
        return context
