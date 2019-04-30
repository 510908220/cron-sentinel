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
        return context


class ServiceItemView(TemplateView):
    template_name = "service/item.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceItemView, self).get_context_data(**kwargs)
        context['title'] =  "xxxx service"

        return context

class ServiceView(TemplateView):
    template_name = "service/main.html"

    def get_context_data(self, **kwargs):
        context = super(ServiceView, self).get_context_data(**kwargs)
        context['title'] =  "service"

        return context

