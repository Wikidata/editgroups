# Generated by Django 2.1.5 on 2019-03-20 09:26

from django.db import migrations
from tagging.batchinspector import BatchInspector
from datetime import datetime

def retag_all_batches(apps, schema_editor):
    BatchInspector().inspect_batches_since(datetime(year=2014,month=1,day=1))

def do_nothing(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('tagging', '0004_retag_edits'),
    ]

    operations = [
        migrations.RunPython(
            retag_all_batches, do_nothing
        ),
    ]