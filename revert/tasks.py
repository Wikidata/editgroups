
from .models import RevertTask
from store.utils import grouper


@shared_task(name='revert_batch')
@run_only_once('task', keys=['pk'], timeout=24*60*60)
def revert_batch(task_pk):
    task = RevertTask.objects.get(pk=task_pk)
    edits = task.batch.edits.filter(reverted=False).order_by('-timestamp')
    for idx, edit in enumerate(edits):
        if idx % 10 == 0:
            task = RevertTask.objects.get(pk=task_pk)
            tokens = task.get_oauth_tokens()
        edit.revert(tokens['oauth_token'], tokens['oauth_token_secret'],
                task.get_summary())
        
    
            

