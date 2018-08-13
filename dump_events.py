import json
import sys
from sseclient import SSEClient as EventSource
from dateutil import parser
from store.stream import WikidataEditStream

if __name__ == '__main__':
    s = WikidataEditStream()
    offset = None
    if len(sys.argv) > 1:
        offset = parser.parse(sys.argv[1])
    for edit in s.stream(offset):
        print(json.dumps(edit))
