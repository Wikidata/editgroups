# Generated by Django 2.0.3 on 2018-03-10 14:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import revert.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('store', '0004_change_uniqueness_constraint'),
    ]

    operations = [
        migrations.CreateModel(
            name='RevertTask',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('uid', models.CharField(default=revert.models.generate_uid, max_length=32)),
                ('comment', models.TextField()),
                ('timestamp', models.DateTimeField(auto_now=True)),
                ('cancel', models.BooleanField(default=False)),
                ('complete', models.BooleanField(default=False)),
                ('batch', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='revert_tasks', to='store.Batch')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
