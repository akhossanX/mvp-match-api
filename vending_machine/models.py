from django.db import models

from django.db.models.deletion import CASCADE
from django.contrib.auth.models import User as DjangoUser


# Create your models here.


class User(models.Model):
    user = models.OneToOneField(DjangoUser, on_delete=models.CASCADE, related_name='user_profile')
    role = models.CharField(max_length=255)


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    cost = models.IntegerField()
    amount_available = models.IntegerField()
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)