
from editgroups.celery import app
from .batchinspector import BatchInspector
from datetime import datetime
from pytz import UTC
from django.conf import settings
from store.models import Batch

@app.task(name='inspect_batches')
def inspect_batches():
    BatchInspector().inspect_batches_since(datetime.utcnow().replace(tzinfo=UTC) - settings.BATCH_INSPECTION_LOOKBEHIND)


@app.task(name='archive_batches')
def archive_batches():
    Batch.archive_old_batches(BatchInspector())
