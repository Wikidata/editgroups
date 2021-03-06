# Generated by Django 2.0.3 on 2018-03-13 15:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('store', '0005_add_editgroups'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.CharField(max_length=128, primary_key=True, serialize=False)),
                ('priority', models.IntegerField(default=0)),
                ('batches', models.ManyToManyField(related_name='tags', to='store.Batch')),
            ],
        ),
    ]
