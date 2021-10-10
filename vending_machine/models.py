from django.contrib.auth.base_user import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import AbstractUser, PermissionsMixin
from django.utils.translation import gettext_lazy as _

from mvp.settings import AUTH_USER_MODEL


class UserRoleChoices(models.TextChoices):
    BUYER = 'buyer'
    SELLER = 'seller'


class CoinChoices(models.IntegerChoices):
    # 5, 10, 20, 50 and 100
    COIN_5 = 5
    COIN_10 = 10
    COIN_20 = 20
    COIN_50 = 50
    COIN_100 = 100


class MyUserManager(BaseUserManager):
    """
    Custom user manager
    override create_user and create_superuser method of BaseUserManager
    """
    def create_user(self, username, password):
        """
        Creates new user and saves it to database
        """
        if not username:
            raise ValueError(_("Users must have a username field"))
        if not password:
            raise ValueError(_("Users must specify a password field"))
        user = self.model(username=username)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None):
        """
        Creates and saves a superuser with the given username and password.
        """
        user = self.create_user(
            username,
            password=password,
        )
        user.is_admin = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):

    username = models.CharField(max_length=255, unique=True)
    role = models.CharField(choices=UserRoleChoices.choices, default=UserRoleChoices.BUYER, max_length=20)
    deposit = models.IntegerField(choices=CoinChoices.choices, default=0)

    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)

    objects = MyUserManager()

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return True

    @property
    def is_staff(self):
        return self.is_admin


class Product(models.Model):
    product_name = models.CharField(max_length=255)
    cost = models.IntegerField()
    amount_available = models.IntegerField(null=True)
    seller = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE)
