#!/usr/bin/env python
import os
import sys
from datetime import datetime
from datetime import timedelta

"""
Amount of time to look back  when restarting
the listener. This helps make sure that we don't
lose any edit when the listener is restarted.
"""
LOOKBEHIND_OFFSET = timedelta(minutes=5)

if __name__ == '__main__':
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "editgroups.settings")
    import django
    django.setup()

    from store.stream import WikiEditStream
    from store.utils import grouper
    from store.models import Edit

    print('Listening to edits...')
    s = WikiEditStream()
    utcnow = datetime.utcnow()
    try:
        latest_edit_seen = Edit.objects.order_by('-timestamp')[0].timestamp
        fetch_from = latest_edit_seen - LOOKBEHIND_OFFSET
    except IndexError:
        fetch_from = None
    print('Starting from offset %s' % fetch_from.isoformat() if fetch_from else 'now')

    for i, batch in enumerate(grouper(s.stream(fetch_from), 50)):
       if i % 50 == 0:
            print('batch %d' % i)
            print(datetime.fromtimestamp(batch[0].get('timestamp')))
       sys.stdout.flush()
       Edit.ingest_edits(batch)

    print('End of stream')

