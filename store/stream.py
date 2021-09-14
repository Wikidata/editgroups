import json
import dateutil
import datetime
from time import sleep
from sseclient import SSEClient as EventSource
import requests

class WikidataEditStream(object):
    def __init__(self):
        self.url = 'https://stream.wikimedia.org/v2/stream/recentchange'
        self.wiki = 'wikidatawiki'

    def stream(self, from_time=None):
        url = self.url
        if from_time is not None:
             url += '?since='+from_time.isoformat().replace('+00:00', 'Z')
        for event in EventSource(url, timeout=30):
            if event.event == 'message':
                try:
                    change = json.loads(event.data)
                    if change.get('wiki') == self.wiki:
                        yield change
                except ValueError:
                    pass


class RecentChangesStream(object):
    """
    Generates an edit stream by polling the recent changes feed
    on the target wiki
    """
    def __init__(self, endpoint_url='https://www.wikidata.org/w/api.php', base='https://www.wikidata.org/entity/'):
        self.url = endpoint_url
        self.base = base
        self.namespaces = [0, 120]

    def stream(self, from_time=None):
        params = {
            'action': 'query',
            'list': 'recentchanges',
            'format': 'json',
            'rcnamespace': '|'.join(str(n) for n in self.namespaces),
            'rcdir': 'newer',
            'rclimit': 500,
            'rctype': 'edit|new|log',
            'rcprop': 'user|comment|parsedcomment|title|ids|sizes|timestamp|flags|loginfo'
        }
        from_time = from_time or datetime.datetime.utcnow()
        start_timestamp = from_time.isoformat().replace('+00:00', 'Z')
        continue_token = None
        previously_seen = set()
        while True:
            try:
                full_params = dict(params)
                if continue_token:
                    full_params['rccontinue'] = continue_token
                elif start_timestamp:
                    full_params['rcstart'] = start_timestamp

                sleep(1)
                r = requests.get(self.url, full_params)
                r.raise_for_status()
                start_timestamp = None
                try:
                    json_payload = r.json()
                    rcids = set()
                    for item in json_payload.get('query', {}).get('recentchanges') or []:
                        rcid = item.get('rcid')
                        rcids.add(rcid)
                        start_timestamp = item.get('timestamp')
                        if rcid not in previously_seen:
                            yield item # self.translate_to_eventstream_json(item)
                        else:
                            print('skipping {}'.format(rcid))
                    continue_token = json_payload.get('continue', {}).get('rccontinue')
                except ValueError as e:
                    print(e)
                    pass
            except requests.exceptions.RequestException as e:
                print(e)
            previously_seen = rcids

    def translate_to_eventstream_json(self, rc_event):
        """
        Translates the representation of an edit obtained form recentchanges
        to the one exposed by the WMF eventstream
        """
        return {
            'type': rc_event.get('type'),
            'meta': {
                'uri': self.base+rc_event.get('title')
            },
            'namespace': rc_event.get('ns'),
            'title': rc_event.get('title'),
            'id': rc_event.get('pageid'),
            'revision': {
                'old': rc_event.get('old_revid'),
                'new': rc_event.get('revid')
            },
            'user': rc_event.get('user'),
            'bot': 'bot' in rc_event,
            'minor': 'minor' in rc_event,
            'length': {
                'old': rc_event.get('oldlen'),
                'new': rc_event.get('newlen')
            },
            'comment': rc_event.get('comment'),
            'parsedcomment': rc_event.get('parsedcomment'),
            'timestamp': int(dateutil.parser.parse(rc_event.get('timestamp')).timestamp()),
            'log_action': rc_event.get('logaction')
        }

