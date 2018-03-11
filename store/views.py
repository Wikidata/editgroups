from django.shortcuts import render
from django.http import Http404

from rest_framework import viewsets
from rest_framework import generics

from .models import Tool
from .models import Edit
from .models import Batch
from .serializers import BatchSimpleSerializer, BatchDetailSerializer, EditSerializer, ToolSerializer

class BatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint listing the latest batches
    """
    queryset = Batch.objects.all().order_by('-started')
    serializer_class = BatchSimpleSerializer
    template_name = 'store/batches.html'


class EditViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Edit.objects.all().order_by('-timestamp')
    serializer_class = EditSerializer

class BatchView(generics.RetrieveAPIView):
    serializer_class = BatchDetailSerializer
    template_name = 'store/batch.html'

    def get_object(self):
        batch_uid = self.kwargs.get('uid')
        tool_code = self.kwargs.get('tool')
        try:
            return Batch.objects.get(uid=batch_uid,tool__shortid=tool_code)
        except Batch.DoesNotExist:
            raise Http404

class BatchesView(generics.ListAPIView):
    serializer_class = BatchSimpleSerializer
    queryset = Batch.objects.all().order_by('-started')
    template_name = 'store/batches.html'

class BatchEditsView(generics.ListAPIView):
    serializer_class = EditSerializer
    model = Edit
    paginate_by = 50
    template_name = 'store/edits.html'

    def get_queryset(self):
        batch_id = self.kwargs.get('id')
        queryset = self.model.objects.filter(batch_id=batch_id).order_by('-timestamp')
        return queryset
