from rest_framework import serializers
from django import db
from .models import Batch
from .models import Edit
from .models import Tool


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ('name', 'shortid', 'url')

class EditSerializer(serializers.ModelSerializer):
    url = serializers.CharField()
    revert_url = serializers.CharField()
    class Meta:
        model = Edit
        fields = '__all__'

class LimitedListSerializer(serializers.ListSerializer):
    """
    A serializer that only prints the most recent children objects
    """
    limit = 10
    model_ordering = '-timestamp'

    def to_representation(self, data):
        iterable = data.all() if isinstance(data, db.models.Manager) else data
        limited_iterable = iterable.order_by(self.model_ordering)[:self.limit]

        return [
            self.child.to_representation(item) for item in limited_iterable
        ]


class LimitedEditSerializer(EditSerializer):
    class Meta:
        model = Edit
        fields = '__all__'
        list_serializer_class = LimitedListSerializer

class BatchSerializer(serializers.ModelSerializer):
    edits = LimitedEditSerializer(many=True, read_only=True)
    tool = ToolSerializer()
    url = serializers.CharField()
    nb_reverted = serializers.IntegerField()

    class Meta:
        model = Batch
        fields = '__all__'
        depth = 1


