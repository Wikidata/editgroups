#-*- coding: utf-8 -*-

from django.db import migrations

def populate_tools(apps, schema_editor):
    Tool = apps.get_model('store', 'Tool')

    tools = [
        Tool(
            name='OpenRefine',
            shortid='OR',
            idregex='.*OR/([a-f0-9]{7}).*',
            idgroupid=1,
            summaryregex='.*\*/ (.*) \(\[\[',
            summarygroupid=1,
            userregex=None,
            usergroupid=0,
            url='https://www.wikidata.org/wiki/Wikidata:OpenRefine',
        ),
        Tool(
            name='QuickStatements',
            shortid='QS',
            idregex='.*\[\[:toollabs:quickstatements/#mode=batch\&batch=(\d+)\|.*',
            idgroupid=1,
            summaryregex='.*(batch).*',
            summarygroupid=1,
            userregex='.* by \[\[User:(.*)\|\]\]',
            usergroupid=1,
            url='https://tools.wmflabs.org/quickstatements/',
        )

    ]

    Tool.objects.bulk_create(tools)

def delete_tools(apps, schema_editor):
    Tool = apps.get_model('store', 'Tool')

    Tool.objects.all().delete()

class Migration(migrations.Migration):
    dependencies = [
        ('store', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_tools, delete_tools)
    ]
