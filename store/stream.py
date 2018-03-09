import json
from sseclient import SSEClient as EventSource

class WikidataEditStream(object):
    def __init__(self):
        self.url = 'https://stream.wikimedia.org/v2/stream/recentchange'
        self.wiki = 'wikidatawiki'

    def stream(self):
        for event in EventSource(self.url):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    if change.get('wiki') == self.wiki:
                        yield change
                except ValueError:
                    pass


