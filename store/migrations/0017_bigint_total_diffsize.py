# Generated by Django 2.1.7 on 2019-04-07 16:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0016_change_batch_manager'),
    ]

    operations = [
        migrations.AlterField(
            model_name='batch',
            name='total_diffsize',
            field=models.BigIntegerField(),
        ),
    ]
