from django.shortcuts import render
from django.shortcuts import get_object_or_404
from django import forms
from django.core.exceptions import ValidationError
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required

from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.generics import CreateAPIView

from store.models import Batch

class CreateRevertTaskForm(forms.Form):
    """
    A form to create a revert task
    """
    tool_shortid = forms.CharField(required=True, hidden=True)
    batch_uid = forms.CharField(required=True, hidden=True)
    comment = forms.CharField(required=True, max_length=150)

    def clean(self):
        try:
            batch = Batch.objects.get(tool__shortid=self.cleaned_data['tool_shortid'],
                                uid=self.cleaned_data['batch_uid'])
            self.cleaned_data['batch'] = batch
        except Batch.DoesNotExist:
            raise ValidationError('Edit batch could not be found.', code='batch-not-found')

        if batch.revert_tasks.filter(canceled=False).exists():
            raise ValidationError('This batch is already being canceled.', code='batch-already-being-canceled')

@login_required
def initiate_revert_task(request, tool, uid):

class RevertTaskView(CreateAPIView):
    """
    The endpoint to start reverting a task
    """
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        batch = get_object_or_404(Batch, tool__shortid=tool, uid=uid)
        form = CreateRevertTaskForm(initial={
            'tool_shortid':tool,
            'batch_uid':uid,
         })
         return render('revert/initiate.html', {'form':form, 'batch':batch})
    
    def create(self, request, format=None):
        form = CreateRevertTaskForm(request.data)
        if !form.is_valid():
            return Response(status=400, form.errors())

        task = RevertTask(
                batch=batch,
                user=request.user,
                comment=form.cleaned_data['comment'])
        task.save()

        return redirect(batch.url)

