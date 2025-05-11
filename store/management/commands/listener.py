#!/usr/bin/env python
import sys
from datetime import datetime
from datetime import timedelta

from django.core.management.base import BaseCommand

from store.stream import WikiEditStream
from store.utils import grouper
from store.models import Edit


class Command(BaseCommand):
    """
    Amount of time to look back  when restarting
    the listener. This helps make sure that we don't
    lose any edit when the listener is restarted.
    """

    LOOKBEHIND_OFFSET = timedelta(minutes=5)
    help = "Listens to edits with EventStream"

    def handle(self, *args, **options):
        print("Listening to edits...")
        s = WikiEditStream()
        try:
            latest_edit_seen = Edit.objects.order_by("-timestamp")[0].timestamp
            fetch_from = latest_edit_seen - self.LOOKBEHIND_OFFSET
        except IndexError:
            fetch_from = None
        offset = fetch_from.isoformat() if fetch_from else "now"
        print("Starting from offset %s" % offset)

        for i, batch in enumerate(grouper(s.stream(fetch_from), 50)):
            if i % 50 == 0:
                print("batch %d" % i)
                print(datetime.fromtimestamp(batch[0].get("timestamp")))
            sys.stdout.flush()
            Edit.ingest_edits(batch)

        print("End of stream")
