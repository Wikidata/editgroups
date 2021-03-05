from rest_framework import serializers
from django import db
from .models import Batch
from .models import Edit
from .models import Tool
from revert.serializers import RevertTaskSerializer
from tagging.serializers import TagSerializer


class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ('name', 'shortid', 'url')

class ToolStatsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ('name', 'shortid', 'url', 'nb_batches', 'nb_unique_users')

    nb_batches = serializers.IntegerField()
    nb_unique_users = serializers.IntegerField()

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
    limit = 11
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

class BatchSimpleSerializer(serializers.ModelSerializer):
    tool = ToolSerializer()
    url = serializers.CharField()
    author = serializers.CharField(source='user')

    editing_speed = serializers.CharField()
    entities_speed = serializers.CharField()

    full_uid = serializers.CharField()
    sorted_tags = TagSerializer(many=True)

    nb_pages = serializers.IntegerField()
    nb_new_pages = serializers.IntegerField()
    nb_existing_pages = serializers.IntegerField()
    nb_reverted = serializers.IntegerField()
    avg_diffsize = serializers.IntegerField()

    duration = serializers.IntegerField()

    class Meta:
        model = Batch
        exclude = ('user',) # translated as 'author'
        depth = 1

class BatchListSerializer(LimitedListSerializer):
    model_ordering = '-started'

class LimitedBatchSimpleSerializer(BatchSimpleSerializer):
    class Meta:
        model = Batch
        fields = '__all__'
        list_serializer_class = BatchListSerializer

class BatchDetailSerializer(serializers.ModelSerializer):
    tool = ToolSerializer()
    url = serializers.CharField()
    author = serializers.CharField(source='user')
    editing_speed = serializers.CharField()
    full_uid = serializers.CharField()
    sorted_tags = TagSerializer(many=True)

    edits = LimitedEditSerializer(many=True, read_only=True)
    entities_speed = serializers.CharField()
    duration = serializers.IntegerField()
    nb_reverted = serializers.IntegerField()
    nb_revertable_edits = serializers.IntegerField()
    nb_pages = serializers.IntegerField()
    nb_new_pages = serializers.IntegerField()
    nb_existing_pages = serializers.IntegerField()
    avg_diffsize = serializers.IntegerField()
    can_be_reverted = serializers.BooleanField()
    archived = serializers.BooleanField()
    reverted_batch = BatchSimpleSerializer()
    reverting_batches = LimitedBatchSimpleSerializer(many=True, read_only=True)

    active_revert_task = RevertTaskSerializer()

    class Meta:
        model = Batch
        exclude = ('user',) # translated as 'author'
        depth = 1


