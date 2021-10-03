from django.conf.urls import url
from django.urls import path

from vending_machine import views

urlpatterns = [
    path('add', views.UserCreateAPIView.as_view(), name='user-add'),
]