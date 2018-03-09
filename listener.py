#!/usr/bin/env python
import os
import sys

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "editgroups.settings")
    import pymysql
    pymysql.install_as_MySQLdb()
    import django
    django.setup()

    from store.stream import WikidataEditStream
    from store.utils import grouper
    from store.models import Edit

    print('Listening to Wikidata edits...')
    s = WikidataEditStream()
    for i, batch in enumerate(grouper(s.stream(), 50)):
       print('batch %d' % i)
       sys.stdout.flush()
       Edit.ingest_edits(batch)

    print('End of stream')

