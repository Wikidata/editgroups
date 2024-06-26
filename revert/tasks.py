
from editgroups.celery import app
from .models import RevertTask
from time import sleep
from store.utils import grouper


@app.task(name='revert_batch')
def revert_batch(task_pk):
    try:
        task = RevertTask.objects.get(pk=task_pk)
        edits = task.batch.edits.filter(reverted=False).order_by('-timestamp').iterator()
        for idx, edit in enumerate(edits):
            if idx % 10 == 0:
                task = RevertTask.objects.get(pk=task_pk)
            task.revert_edit(edit)
            sleep(1)
    finally:
        task.complete = True
        task.save(update_fields=['complete'])

