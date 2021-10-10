from django.contrib.auth import get_user_model
from rest_framework import serializers
from vending_machine.models import User, Product


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=50, min_length=6, write_only=True, allow_blank=False
    )
    id = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = ('id', 'username', 'password', 'deposit', 'role')

    def create(self, validated_data):
        _user = User(**validated_data)
        _user.set_password(validated_data['password'])
        _user.save()
        return _user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)

        for (key, value) in validated_data.items():
            setattr(instance, key, value)

        if password is not None:
            instance.set_password(password)

        instance.save()
        return instance


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ('id', 'product_name', 'seller', 'cost', 'amount_available')
