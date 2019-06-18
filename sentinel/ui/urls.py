from django.urls import path

from .views import DashboardView, ServiceItemView, ServiceView, PingView, AlertView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(DashboardView.as_view()), name='dashboard'),
    path('service/<slug:id>/', login_required(ServiceItemView.as_view()),
         name='service-item-view'),
    path('service/', login_required(ServiceView.as_view()), name='service-view'),
    path('alert/', login_required(AlertView.as_view()), name='alert-view'),
    path('ping/', login_required(PingView.as_view()), name='ping-view'),

]
