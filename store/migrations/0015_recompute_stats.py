# Generated by Django 2.0.3 on 2018-03-13 17:05

from django.db import migrations, models
import sys


def compute_diffsizes(apps, schema_editor):
    Batch = apps.get_model('store', 'Batch')
    for idx, batch in enumerate(Batch.objects.all().order_by('-ended').iterator()):
        if idx % 1000 == 0:
            print(idx)
            sys.stdout.flush()
        batch.nb_edits = batch.edits.count()
        batch.nb_distinct_pages = batch.edits.all().values('title').distinct().count()
        batch.nb_reverted_edits = batch.edits.all().filter(reverted=True).count()
        batch.nb_new_pages = batch.edits.all().filter(changetype='new').count()
        batch.total_diffsize = batch.edits.all().aggregate(total_diff=models.Sum('newlength')-models.Sum('oldlength')).get('total_diff')
        batch.save()

def do_nothing(apps, schema_editor):
    pass

class Migration(migrations.Migration):
    atomic = False

    dependencies = [
        ('store', '0014_recompute_diffsizes'),
    ]

    operations = [
        migrations.RunPython(
            compute_diffsizes, do_nothing
        ),
    ]
