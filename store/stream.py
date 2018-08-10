import json
from sseclient import SSEClient as EventSource

class WikidataEditStream(object):
    def __init__(self):
        self.url = 'https://stream.wikimedia.org/v2/stream/recentchange'
        self.wiki = 'wikidatawiki'

    def latest_offset(self):
        """
        Returns the offset of the latest event
        """
        for event in self.stream():
            return event.get('meta', {}).get('offset')

    def stream(self, last_id=None):
        last_id_json = None
        if last_id is not None:
             last_id_json = json.dumps({'offset':offset,'topic':'eqiad.mediawiki.recentchange','partition':0})
        for event in EventSource(self.url, last_id=last_id_json):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    if change.get('wiki') == self.wiki:
                        yield change
                except ValueError:
                    pass


