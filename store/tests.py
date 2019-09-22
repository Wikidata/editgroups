
from datetime import datetime
import unittest
from pytz import UTC
import html5lib

from django.conf import settings
from django.test import TestCase
from django.test import Client
from django.urls import reverse
from rest_framework.test import APITestCase
from caching import invalidation

from .models import Tool
from .models import Edit
from .models import Batch
from .stream import WikidataEditStream
from tagging.utils import FileBasedDiffInspector
from tagging.utils import BatchInspectorStub
from revert.models import RevertTask
from django.contrib.auth.models import User

class ToolTest(TestCase):
    def setUp(self):
        invalidation.cache.clear()

    def test_or(self):
        tool = Tool.objects.get(shortid='OR')

        self.assertEquals(('ca7d7cc', 'Pintoch', 'import Charity Navigator'),
            tool.match("Pintoch",
                "/* wbeditentity-update:0| */ import Charity Navigator ([[Wikidata:Edit groups/OR/ca7d7cc|discuss]])"))

    def test_match_without_summary(self):
        tool = Tool.objects.get(shortid='OR')

        self.assertEquals(('ca7d7cc', 'Pintoch', ''),
            tool.match("Pintoch",
                "/* wbeditentity-update:0| */ ([[Wikidata:Edit groups/OR/ca7d7cc|discuss]])"))

    def test_or_setclaim(self):
        tool = Tool.objects.get(shortid='OR')
        self.assertEquals(('3990c0d', 'Pintoch', 'add EIN ids from Charity Navigator'),
             tool.match("Pintoch",
                "/* wbsetclaim-create:2||1 */ [[Property:P1297]]: 88-0302673, add EIN ids from Charity Navigator ([[:toollabs:editgroups/b/OR/3990c0d|details]])"))


    def test_qs(self):
        tool = Tool.objects.get(shortid='QSv2')

        self.assertEquals(('2120', 'Pintoch', '#quickstatements'),
            tool.match("QuickStatementsBot",
                "/* wbcreateclaim-create:1| */ [[Property:P3896]]: Data:Neighbourhoods/New York City.map, #quickstatements; [[:toollabs:quickstatements/#mode=batch&batch=2120|batch #2120]] by [[User:Pintoch|]]"))

    def test_eg(self):
        tool = Tool.objects.get(shortid='EG')

        self.assertEquals(('c367abf', 'Pintoch', 'this was just dumb'),
            tool.match("Pintoch", "/* undo:0||1234|Rageux */ this was just dumb ([[:toollabs:editgroups/b/EG/c367abf|details]])"))

        # for deletions, undeletions
        self.assertEquals(('c367abf', 'Pintoch', 'deleting gibberish items'),
            tool.match("Pintoch", "deleting gibberish items ([[:toollabs:editgroups/b/EG/c367abf|details]])"))


class EditTest(TestCase):
    def setUp(self):
        invalidation.cache.clear()
        diff_inspector = FileBasedDiffInspector('store/testdata/diffs/')
        self.batch_inspector = BatchInspectorStub(diff_inspector=diff_inspector)

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
        self.assertEquals(0, batch.nb_reverted_edits)
        self.assertEquals(0, batch.nb_new_pages)
        self.assertEquals('32.9', batch.editing_speed)

    def test_recompute_stats(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        self.assertEquals(1, Batch.objects.count())
        # Mess around with the editing statistics
        batch = Batch.objects.get()
        batch.nb_edits = 0
        batch.nb_new_pages = 12
        batch.nb_reverted_edits = 389
        batch.nb_distinct_pages = 32
        batch.save()

        # Update them
        batch.recompute_cached_stats()
        self.assertEqual(51, batch.nb_edits)
        self.assertEqual(0, batch.nb_reverted_edits)
        self.assertEqual(0, batch.nb_new_pages)
        self.assertEqual(51, batch.nb_distinct_pages)

    def test_duration(self):
        tool = Tool.objects.get(shortid='OR')
        b = Batch(tool=tool, user='MyUser', uid='e839fda2', summary='hello',
            started=datetime(2018, 3, 3, 16, 39, 37, tzinfo=UTC),
            ended=datetime(2018, 3, 6, 16, 39, 37, tzinfo=UTC),
            nb_edits=4)
        self.assertEquals(b.duration, 3*24*3600)

    def test_ingest_eg(self):
        Edit.ingest_jsonlines('store/testdata/eg_revert.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('EG', batch.tool.shortid)
        self.assertEquals(0, batch.nb_reverted_edits)
        self.assertEquals(0, batch.nb_new_pages)

    def test_ingest_twice(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(51, batch.nb_edits)
        self.assertEquals(0, batch.nb_reverted_edits)
        self.assertEquals(0, batch.nb_new_pages)

    def test_ingest_new_items(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_new_items.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(82, batch.nb_edits)
        self.assertEquals(9, batch.nb_new_pages)
        self.assertEquals(9, batch.nb_pages)
        self.assertEquals(0, batch.nb_existing_pages)
        self.assertEquals(0, batch.nb_reverted_edits)

    def test_ingest_new_items_twice(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_new_items.json')
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_new_items.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(82, batch.nb_edits)
        self.assertEquals(9, batch.nb_new_pages)
        self.assertEquals(9, batch.nb_pages)
        self.assertEquals(0, batch.nb_existing_pages)
        self.assertEquals(0, batch.nb_reverted_edits)

    def test_hijack(self):
        """
        Someone trying to reuse the token to artificially attribute
        edits to a batch
        """
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        Edit.ingest_jsonlines('store/testdata/hijack.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(51, batch.nb_edits)

    def test_archive(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        batch = Batch.objects.get()
        self.assertEquals(51, batch.nb_edits)
        self.assertEquals(0, batch.nb_new_pages)
        self.assertEquals(130901, batch.total_diffsize)
        self.assertEquals(datetime(2018, 3, 6, 16, 39, 37, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 6, 16, 41, 10, tzinfo=UTC), batch.ended)
        self.assertEquals(51, batch.edits.count())
        self.assertFalse(batch.archived)
        self.assertTrue(batch.can_be_reverted)

        # Mess up with the statistics a bit
        batch.nb_edits = 42
        batch.nb_new_pages = 42
        batch.save()

        batch.archive(self.batch_inspector)

        batch = Batch.objects.get()

        # The correct statistics have been recomputed
        self.assertEquals(51, batch.nb_edits)
        self.assertEquals(0, batch.nb_new_pages)
        self.assertEquals(130901, batch.total_diffsize)
        self.assertEquals(datetime(2018, 3, 6, 16, 39, 37, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 6, 16, 41, 10, tzinfo=UTC), batch.ended)
        self.assertTrue(batch.archived)
        self.assertFalse(batch.can_be_reverted)

        # Most edits were deleted
        self.assertEquals(settings.EDITS_KEPT_AFTER_ARCHIVAL, batch.edits.count())

        # If we attempt to archive again, the statistics will not be recomputed
        batch.archive(self.batch_inspector)
        self.assertTrue(batch.archived)
        self.assertEquals(51, batch.nb_edits)

    def test_archive_small_batch(self):
        # There is no point in archiving small batches
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')
        batch = Batch.objects.get()
        batch.archive(self.batch_inspector)
        self.assertFalse(batch.archived)
        self.assertTrue(batch.can_be_reverted)

    def test_archive_old_batches(self):
        """
        Old batches get archived periodically
        """
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        Batch.archive_old_batches(self.batch_inspector)
        batch = Batch.objects.get()
        self.assertTrue(batch.archived)

    def test_wrong_namespace(self):
        """
        Only edits in the item and property namespaces are considered
        """
        Edit.ingest_jsonlines('store/testdata/wrong_namespace.json')
        self.assertEquals(0, Batch.objects.count())

    def test_ingest_jsonlines_qs(self):
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals('QSv2', batch.tool.shortid)
        self.assertEquals('Pintoch', batch.user)
        self.assertEquals('2120', batch.uid)
        self.assertEquals(datetime(2018, 3, 7, 16, 20, 12, tzinfo=UTC), batch.started)
        self.assertEquals(datetime(2018, 3, 7, 16, 20, 14, tzinfo=UTC), batch.ended)
        self.assertEquals(4, batch.nb_edits)
        self.assertEquals(1, batch.nb_pages)

    def test_reverts(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_reverts.json')

        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(5, batch.nb_edits)
        self.assertEquals(2, batch.nb_reverted)
        self.assertEquals(1, batch.nb_pages)

    def test_deletions(self):
        Edit.ingest_jsonlines('store/testdata/new_items_deleted.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(1, batch.nb_new_pages)
        self.assertEqual(1, batch.nb_reverted)
        self.assertEquals(1, batch.nb_pages)

    def test_deletion_batch(self):
        Edit.ingest_jsonlines('store/testdata/deletion_edit.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(0, batch.nb_new_pages)
        self.assertEqual(0, batch.nb_reverted)

    def test_deletion_restore(self):
        Edit.ingest_jsonlines('store/testdata/deletion_restore.json')
        self.assertEquals(2, Batch.objects.count())
        delete_batch = Edit.objects.get(changetype='delete').batch
        restore_batch = Edit.objects.get(changetype='restore').batch
        self.assertEquals(1, delete_batch.nb_reverted)
        self.assertEqual(0, restore_batch.nb_reverted)
        self.assertEqual(1, restore_batch.nb_undeleted_new_pages)

    def test_new_deletion_restore_deletion(self):
        Edit.ingest_jsonlines('store/testdata/new_deletion_restore_deletion.json')
        self.assertEquals(4, Batch.objects.count())
        new_batch = Edit.objects.get(changetype='new').batch
        restore_batch = Edit.objects.get(changetype='restore').batch
        self.assertEquals(1, new_batch.nb_reverted)
        self.assertEqual(1, restore_batch.nb_reverted)
        self.assertEqual(Edit.objects.filter(reverted=False).count(), 1)

        # This relies on the RevertTask model
        user = User.objects.create_user('fabio', 'fabio@futureproof.io', 'babebibobu')
        rt1 = RevertTask(uid='be3a1d9', batch=new_batch, user=user, comment="I really don't like this item")
        rt1.save()
        rt2 = RevertTask(uid='45bc44f', batch=restore_batch, user=user, comment="I insist, this item sucks")
        rt2.save()

        self.assertEqual(len(new_batch.reverting_batches), 1)
        first_reverting_batch = new_batch.reverting_batches[0]
        self.assertEqual(first_reverting_batch.reverted_batch, new_batch)
        self.assertEqual(len(restore_batch.reverting_batches), 1)
        second_reverting_batch = restore_batch.reverting_batches[0]
        self.assertEqual(second_reverting_batch.reverted_batch, restore_batch)

    def test_str(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')

        edit = Edit.objects.all().order_by('timestamp')[0]
        self.assertEquals('https://www.wikidata.org/wiki/index.php?diff={newrevid}&oldid={oldrevid}'.format(
                newrevid=edit.newrevid, oldrevid=edit.oldrevid), edit.url)
        self.assertEquals('<Edit {url} >'.format(url=edit.url), str(edit))

    def test_current_lag(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        current_lag = Edit.current_lag()
        self.assertTrue(current_lag.seconds > 1)

    def test_current_lag_no_edit(self):
        current_lag = Edit.current_lag()
        self.assertTrue(current_lag.total_seconds() < 1)

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

class PagesTest(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.client = Client()
        cls.parser = html5lib.HTMLParser(strict=True)
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        cls.batch = Batch.objects.get()
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')

    def get_page(self, url_name, **kwargs):
        return self.client.get(reverse(url_name, kwargs or None))

    def check_html(self, response):
        self.assertEqual(200, response.status_code)
        self.parser.parse(response.content)

    def test_batches_list(self):
        response = self.get_page('list-batches')
        self.check_html(response)

    def test_batches_list_filtered(self):
        response = self.client.get(reverse('list-batches')+'?tool=OR')
        self.check_html(response)
        tag = self.batch.tags.all()[0]
        response = self.client.get(reverse('list-batches')+'?tool=OR&tags='+tag.id)
        self.check_html(response)

    def test_batch(self):
        response = self.client.get(self.batch.url)
        self.check_html(response)

    def test_batch_404(self):
        response = self.client.get('/b/ST/3849384/')
        self.assertEqual(404, response.status_code)

    @classmethod
    def tearDownClass(cls):
        Batch.objects.all().delete()
