from django.shortcuts import render
from django.http import Http404

from rest_framework import viewsets
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.renderers import JSONRenderer
from rest_framework.renderers import BrowsableAPIRenderer

from .models import Tool
from .models import Edit
from .models import Batch
from .serializers import BatchSimpleSerializer, BatchDetailSerializer, EditSerializer, ToolSerializer
from django_filters.rest_framework import DjangoFilterBackend
from tagging.filters import TaggingFilterBackend

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

    # Manual bypass for 404 pages for batches
    def get(self, *args, **kwargs):
        try:
            return super(BatchView, self).get(*args, **kwargs)
        except Http404 as e:
            ctxt = {
                'uid':self.kwargs.get('uid'),
                'current_lag': int(Edit.current_lag().total_seconds()),
            }
            return Response(ctxt, template_name='store/batch-not-found.html', status=404)

class APIBatchView(BatchView):
    """
    Gives details about a particular batch
    """
    renderer_classes = (JSONRenderer,BrowsableAPIRenderer)

class BatchesView(generics.ListAPIView):
    serializer_class = BatchSimpleSerializer
    queryset = Batch.objects.all().order_by('-ended')
    template_name = 'store/batches.html'
    filter_fields = ('user',)
    filter_backends = (TaggingFilterBackend,)

class APIBatchesView(BatchesView):
    """
    Lists the latest batches, by inverse date of last edit.
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
