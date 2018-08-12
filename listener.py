#!/usr/bin/env python
import os
import sys
from datetime import datetime
from datetime import timedelta

"""
Number of seconds to look back when restarting
the listener. This helps make sure that we don't
lose any edit when the listener is restarted.

10000 amounts to about 5 minutes of looking back.
"""
LOOKBEHIND_OFFSET = timedelta(days=1)

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
    utcnow = datetime.utcnow()
    fetch_from = utcnow - LOOKBEHIND_OFFSET
    print('Starting from offset %s' % fetch_from.isoformat())

    for i, batch in enumerate(grouper(s.stream(fetch_from), 50)):
       if i % 50 == 0:
            print('batch %d' % i)
       sys.stdout.flush()
       Edit.ingest_edits(batch)

    print('End of stream')

