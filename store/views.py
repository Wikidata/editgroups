from django.shortcuts import render
from django.http import Http404

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.renderers import JSONRenderer
from rest_framework.renderers import BrowsableAPIRenderer

from .models import Tool
from .models import Edit
from .models import Batch
from .serializers import BatchSimpleSerializer, BatchDetailSerializer, EditSerializer, ToolSerializer

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

class APIBatchView(BatchView):
    """
    Gives details about a particular batch
    """
    renderer_classes = (JSONRenderer,BrowsableAPIRenderer)

class BatchesView(generics.ListAPIView):
    serializer_class = BatchSimpleSerializer
    queryset = Batch.objects.all().order_by('-started')
    template_name = 'store/batches.html'

class APIBatchesView(BatchesView):
    """
    Lists the latest batches, by inverse date of creation.
    """
    renderer_classes = (JSONRenderer,BrowsableAPIRenderer)

class BatchEditsView(generics.ListAPIView):
    serializer_class = EditSerializer
    model = Edit
    paginate_by = 50
    template_name = 'store/edits.html'

    def get_queryset(self):
        batch_uid = self.kwargs.get('uid')
        tool_shortid = self.kwargs.get('tool')
        try:
            batch = Batch.objects.get(uid=batch_uid,tool__shortid=tool_shortid)
        except Batch.DoesNotExist:
            raise Http404

        queryset = batch.edits.order_by('-timestamp')
        return queryset

class APIBatchEditsView(BatchEditsView):
    """
    Lists the edits in a particular batch
    """
    renderer_classes = (JSONRenderer,BrowsableAPIRenderer)
