import json
from sseclient import SSEClient as EventSource

class WikidataEditStream(object):
    def __init__(self):
        self.url = 'https://stream.wikimedia.org/v2/stream/recentchange'
        self.wiki = 'wikidatawiki'

    def stream(self, from_time=None):
        last_id_str = None
        if from_time is not None:
             last_id_str = json.dumps([{'timestamp':int(from_time.timestamp()),'topic':'eqiad.mediawiki.recentchange','partition':0}])
        for event in EventSource(self.url, last_id=last_id_str):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    if change.get('wiki') == self.wiki:
                        yield change
                except ValueError:
                    pass


