from django.conf.urls import url
from django.urls import path

from vending_machine import views

urlpatterns = [
    # path('add', views.UserCreateAPIView.as_view(), name='user-add'),
    # path('example', views.example_view, name='example'),
    path('user', views.user_create, name='user-create'),
    path('user/<int:pk>', views.user_detail, name='user-detail'),
    path('users', views.user_list, name='users-list'),
    path('product', views.product_create, name='product-create'),
    path('products', views.product_list, name='product-list'),
    path('product/<int:pk>', views.product_detail, name='product-detail'),
    path('deposit/<int:amount>', views.deposit, name='deposit'),
    path('buy', views.buy, name='buy'),
    path('reset', views.reset, name='reset'),
]
