from rest_framework import serializers
from .models import Tag


class TagSerializer(serializers.ModelSerializer):
    display_name = serializers.CharField()

    class Meta:
        model = Tag
        fields = ('id', 'priority', 'display_name', 'color', 'category', 'code')


