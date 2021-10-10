from django.contrib.auth import authenticate
from django.db import models
from rest_framework.authtoken.models import Token

from vending_machine.models import User, Product


def create_user(credentials: dict, **kwargs):
    user = User.objects.create_user(**credentials)
    user.role = kwargs.get('role', 'buyer')
    user.deposit = kwargs.get('deposit', 0)
    user.save()
    return user


def bulk_create_users(users_list: list):
    for user in users_list:
        create_user(credentials=user)


def authenticate_user(username="", password=""):
    _user = authenticate(username=username, password=password)
    _token = ''
    if _user:
        _token, _ = Token.objects.get_or_create(user=_user)

    return _user, _token


def bulk_create_products(seller, products_list=[]):
    products = []
    for product in products_list:
        prod = Product.objects.create(**product, seller=seller)
        products.append({
            "id": prod.id,
            "product_name": prod.product_name,
            "cost": prod.cost,
            "amount_available": prod.amount_available,
            "seller": prod.seller.id,
        })

    return products
