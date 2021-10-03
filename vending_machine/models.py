from django.db import models

# Create your models here.


class User(models.Model):

    class DepositChoices(models.IntegerChoices):
        COIN_ZERO = 0  # Default deposit upon user creation or if no deposit is supplied
        COIN_FIVE = 5
        COIN_TEN = 10
        COIN_TWENTY = 20
        COIN_FIFTY = 50
        COIN_HUNDRED = 100

    class UserRoleChoices(models.TextChoices):
        SELLER = 'seller'
        BUYER = 'buyer'

    username = models.CharField(max_length=255, unique=True, blank=False)
    password = models.CharField(max_length=255, blank=False)
    deposit = models.IntegerField(
        choices=DepositChoices.choices,
        default=0,
        null=False
    )
    role = models.CharField(
        max_length=255,
        choices=UserRoleChoices.choices,
        default='buyer',
        null=False
    )


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    cost = models.IntegerField()
    amount_available = models.IntegerField()
    seller_id = models.ForeignKey(User, on_delete=models.CASCADE)
