
from datetime import datetime
import unittest
from pytz import UTC

from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Tool
from .models import Edit
from .models import Batch
from .stream import WikidataEditStream

class ToolTest(TestCase):

    def test_or(self):
        tool = Tool.objects.get(shortid='OR')

        self.assertEquals(('ca7d7cc', 'Pintoch', 'import Charity Navigator'),
            tool.match("Pintoch",
                "/* wbeditentity-update:0| */ import Charity Navigator ([[Wikidata:Edit groups/OR/ca7d7cc|discuss]])"))

    def test_or_setclaim(self):
        tool = Tool.objects.get(shortid='OR')
        self.assertEquals(('3990c0d', 'Pintoch', 'add EIN ids from Charity Navigator'),
             tool.match("Pintoch",
                "/* wbsetclaim-create:2||1 */ [[Property:P1297]]: 88-0302673, add EIN ids from Charity Navigator ([[:toollabs:editgroups/b/OR/3990c0d|details]])"))


    def test_qs(self):
        tool = Tool.objects.get(shortid='QS')

        self.assertEquals(('2120', 'Pintoch', '#quickstatements'),
            tool.match("QuickStatementsBot",
                "/* wbcreateclaim-create:1| */ [[Property:P3896]]: Data:Neighbourhoods/New York City.map, #quickstatements; [[:toollabs:quickstatements/#mode=batch&batch=2120|batch #2120]] by [[User:Pintoch|]]"))


class EditTest(TestCase):
    def test_ingest_jsonlines_or(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('OR', batch.tool.shortid)
        self.assertEquals('Pintoch', batch.user)
        self.assertEquals('ca7d7cc', batch.uid)
        self.assertEquals(datetime(2018, 3, 6, 16, 39, 37, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 6, 16, 41, 10, tzinfo=UTC), batch.ended)
        self.assertEquals(51, batch.nb_edits)

    def test_ingest_twice(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(51, batch.nb_edits)

    def test_ingest_jsonlines_qs(self):
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('QS', batch.tool.shortid)
        self.assertEquals('Pintoch', batch.user)
        self.assertEquals('2120', batch.uid)
        self.assertEquals(datetime(2018, 3, 7, 16, 20, 12, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 7, 16, 20, 14, tzinfo=UTC), batch.ended)
        self.assertEquals(4, batch.nb_edits)

    def test_reverts(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_reverts.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(5, batch.nb_edits)
        self.assertEquals(2, batch.nb_reverted)

    def test_str(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        edit = Edit.objects.all().order_by('timestamp')[0]
        self.assertEquals('https://www.wikidata.org/wiki/index.php?diff=644512815&oldid=376870215', edit.url)
        self.assertEquals('<Edit https://www.wikidata.org/wiki/index.php?diff=644512815&oldid=376870215 >', str(edit))

class BatchEditsViewTest(APITestCase):
    @classmethod
    def setUpClass(cls):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        cls.batch = Batch.objects.get()

    def test_nbpages(self):
        self.assertEquals(51, self.batch.nb_pages)

    def test_avg_diffsize(self):
        self.assertTrue(2500 < self.batch.avg_diffsize)
        self.assertTrue(self.batch.avg_diffsize < 3000)

    def pagination(self):
        response = self.client.get(reverse('batch-edits', args=[self.batch.id]))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.batch.edit_set.count(), response.data['count'])

    @classmethod
    def tearDownClass(cls):
        Batch.objects.all().delete()

class WikidataEditStreamTest(unittest.TestCase):
    def test_stream(self):
        s = WikidataEditStream()
        for idx, edit in enumerate(s.stream()):
            if idx > 10:
                break
            self.assertEquals('wikidatawiki', edit['wiki'])
