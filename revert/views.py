from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView
from rest_framework.generics import DestroyAPIView

from store.models import Batch
from store.serializers import BatchDetailSerializer
from store.templatetags.isadmin import isadmin
from .models import RevertTask

class CreateRevertTaskForm(forms.Form):
    """
    A form to create a revert task
    """
    comment = forms.CharField(required=True, max_length=150, widget=forms.TextInput(attrs={'placeholder': 'describe why you are undoing this group'}))

    def __init__(self, batch, user, *args, **kwargs):
        super(CreateRevertTaskForm, self).__init__(*args, **kwargs)
        self.batch = batch
        self.user = user

    def clean(self):
        super(CreateRevertTaskForm, self).clean()
        if self.batch.active_revert_task is not None:
            raise ValidationError('This batch is already being canceled.',
                code='batch-already-being-canceled')
        if not self.batch.nb_revertable_edits:
            raise ValidationError('This batch does not have any edit that can be undone.',
                code='nothing-to-undo')
        if self.batch.nb_undeleted_new_pages and not isadmin(user):
            raise ValidationError('Undoing this batch requires admin privileges.')


@login_required
def initiate_revert_view(request, tool, uid):
    batch = get_object_or_404(Batch, tool__shortid=tool, uid=uid)
    form = CreateRevertTaskForm(batch, initial={
        'tool_shortid':tool,
        'batch_uid':uid,
    })
    return render(request, 'revert/initiate.html', {'form':form, 'batch':batch})


class RevertTaskView(CreateAPIView):
    """
    The endpoint to start reverting a task
    """
    permission_classes = (IsAuthenticated,)
    template_name = 'revert/initiate.html'

    def create(self, request, tool, uid, format=None):
        batch = get_object_or_404(Batch, tool__shortid=tool, uid=uid)
        form = CreateRevertTaskForm(batch, request.user, request.data)
        if not form.is_valid():
            return Response(status=400, data={'form':form, 'batch':form.batch})

        task = RevertTask(
                batch=form.batch,
                user=request.user,
                comment=form.cleaned_data['comment'])
        task.save()

        from .tasks import revert_batch
        revert_batch.apply_async(args=[task.id])

        return redirect(form.batch.url)

class StopRevertTaskView(CreateAPIView):
    """
    The endpoint to stop reverting a task
    """
    permission_classes = (IsAuthenticated,)
    template_name = 'store/batch.html'

    def create(self, request, tool, uid, format=None):
        batch = get_object_or_404(Batch, tool__shortid=tool, uid=uid)
        task = batch.active_revert_task
        if task is None:
            return Response(status=404, data=BatchDetailSerializer(batch).data)

        if task.user_id != request.user.id:
            return Response(status=403, data=BatchDetailSerializer(batch).data)

        task.cancel = True
        task.save(update_fields=['cancel'])

        return redirect(batch.url)

