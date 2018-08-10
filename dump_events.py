import json
import sys
from sseclient import SSEClient as EventSource

class WikidataEditStream(object):
    def __init__(self):
        self.url = 'https://stream.wikimedia.org/v2/stream/recentchange'
        self.wiki = 'wikidatawiki'

    def streamEdits(self):
        offset = None
        pattern = None
        if len(sys.argv) > 1:
            offset = int(sys.argv[1])
            generator = EventSource(self.url,
                last_id=json.dumps([{'offset':offset,"topic": "eqiad.mediawiki.recentchange","partition":0}]))
        else:
            generator = EventSource(self.url)

        if len(sys.argv) > 2:
            pattern = sys.argv[2]

        for event in generator:
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    if change.get('wiki') == self.wiki and (pattern is None or pattern in event.data):
                        yield change
                except ValueError:
                    pass

if __name__ == '__main__':
    s = WikidataEditStream()
    for edit in s.streamEdits():
        print(json.dumps(edit))
