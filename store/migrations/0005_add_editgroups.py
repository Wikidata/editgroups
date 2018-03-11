#-*- coding: utf-8 -*-

from django.db import migrations

def populate_tools(apps, schema_editor):
    Tool = apps.get_model('store', 'Tool')

    tools = [
        Tool(
            name='EditGroups',
            shortid='EG',
            idregex='.*EG/([a-f0-9]{7}).*',
            idgroupid=1,
            summaryregex='.*\*/ (.*) \(\[\[',
            summarygroupid=1,
            userregex=None,
            usergroupid=0,
            url='https://tools.wmflabs.org/editgroups/',
        ),
    ]

    Tool.objects.bulk_create(tools)

def delete_tools(apps, schema_editor):
    Tool = apps.get_model('store', 'Tool')

    Tool.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0004_change_uniqueness_constraint'),
    ]

    operations = [
        migrations.RunPython(populate_tools, delete_tools)
    ]
