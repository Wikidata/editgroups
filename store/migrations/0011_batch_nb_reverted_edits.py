# Generated by Django 2.1 on 2018-12-06 08:54

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0010_recompute_nb_pages'),
    ]

    operations = [
        migrations.AddField(
            model_name='batch',
            name='nb_reverted_edits',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='batch',
            name='nb_new_pages',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),

    ]
