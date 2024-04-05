# serializers.py

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Wallet


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    class Meta:
        model = User
        # fields = ['username', 'password']
        fields = ['username', 'password', 'email', 'first_name', 'last_name']




class WalletSerializer(serializers.ModelSerializer):
    class Meta:
        model = Wallet
        fields = ['id', 'balance', 'saving_activated']
