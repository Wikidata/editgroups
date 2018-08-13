import json
from sseclient import SSEClient as EventSource

class WikidataEditStream(object):
    def __init__(self):
        self.url = 'https://stream.wikimedia.org/v2/stream/recentchange'
        self.wiki = 'wikidatawiki'

    def stream(self, from_time=None):
        url = self.url
        if from_time is not None:
             url += '?since='+from_time.isoformat().replace('+00:00', 'Z')
        for event in EventSource(url)::
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    if change.get('wiki') == self.wiki:
                        yield change
                except ValueError:
                    pass


