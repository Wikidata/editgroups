from rest_framework import serializers
from django import db
from django.contrib.auth.models import User
from .models import RevertTask

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username','id')

class RevertTaskSerializer(serializers.ModelSerializer):
    author = UserSerializer(source='user')

    class Meta:
        model = RevertTask
        exclude = ('user',)

