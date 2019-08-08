import os.path
from .diffinspector import DiffInspector
from .batchinspector import BatchInspector

class MockDiffInspector(DiffInspector):
    """
    A simple diff inspector where we can manually store
    the pre-set responses given two revision ids
    """

    def __init__(self):
        super(MockDiffInspector, self).__init__()
        self.responses = {}

    def _retrieve_html_diff(self, oldrevid, newrevid):
        return self.responses.get((oldrevid, newrevid))

class FileBasedDiffInspector(DiffInspector):
    """
    A diff inspector which loads its responses from a file
    cache.
    """

    def __init__(self, directory):
        super(FileBasedDiffInspector, self).__init__()
        self.directory = directory

    def _retrieve_html_diff(self, oldrevid, newrevid):
        filename = os.path.join(self.directory, '{}_{}.json'.format(oldrevid, newrevid))
        if os.path.isfile(filename):
            with open(filename, 'r') as f:
                return f.read()
        else:
            result = super(FileBasedDiffInspector, self)._retrieve_html_diff(oldrevid, newrevid)
            with open(filename, 'w') as f:
                f.write(result)
            return result

class BatchInspectorStub(BatchInspector):
    requests_delay = 0


