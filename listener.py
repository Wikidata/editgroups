#!/usr/bin/env python
import os
import sys

"""
Number of seconds to look back when restarting
the listener. This helps make sure that we don't
lose any edit when the listener is restarted.

10000 amounts to about 5 minutes of looking back.
"""
LOOKBEHIND_OFFSET = 10000

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
    last_offset = s.last_offset()
    fetching_offset = last_offset - LOOKBEHIND_OFFSET
    print('Starting from offset %d' % fetching_offset)

    for i, batch in enumerate(grouper(s.stream(fetching_offset), 50)):
       if i % 50 == 0:
            print('batch %d' % i)
       sys.stdout.flush()
       Edit.ingest_edits(batch)

    print('End of stream')

