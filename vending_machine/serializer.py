from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from .models import *


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=50, min_length=6, write_only=True, allow_blank=False
    )

    class Meta:
        model = User
        fields = '__all__'

    def create(self, validated_data):
        # Hash the password if It is supplied
        if 'password' in validated_data:
            validated_data['password'] = make_password(validated_data['password'])

        return User.objects.create(**validated_data)


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
