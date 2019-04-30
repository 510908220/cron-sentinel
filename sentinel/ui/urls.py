from django.urls import path

from .views import DashboardView,ServiceItemView,ServiceView
from django.contrib.auth.decorators import login_required

urlpatterns = [
    path('', login_required(DashboardView.as_view()), name='dashboard'),
    path('service/<int:id>/', login_required(ServiceItemView.as_view()), name='service-item-view'),
    path('service/', login_required(ServiceView.as_view()), name='service-view'),
]












