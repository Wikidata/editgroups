from django.test import TestCase
from store.models import Edit
from store.models import Batch
from .models import Tag
from .models import action_re
from .models import language_re
from caching import invalidation

cache = invalidation.cache

class TagTest(TestCase):
    def setUp(self):
        cache.clear()

    def test_action_re(self):
        self.assertEquals('wbsetdescription-add', action_re.match('/* wbsetdescription-add:1|eu */ Indonesiako herria, #quickstatements').group(1))

    def test_extract(self):
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')
        batch = Batch.objects.get()
        last_edit = batch.edits.order_by('-timestamp')[0]
        # tag extraction on the latest edit does not return any *new* tag
        self.assertEquals([], [tag.id for tag in Tag.extract(last_edit)])
        self.assertEquals(['wbcreateclaim-create'], list(batch.tag_ids))

    def test_extract_editentity(self):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        batch = Batch.objects.get()
        self.assertEquals(['wbeditentity-update'], list(batch.tag_ids))

    def test_tag_former_batches(self):
        Edit.ingest_jsonlines('store/testdata/one_qs_batch.json')
        Tag.objects.all().delete()
        Tag.retag_all_batches()
        batch = Batch.objects.get()
        self.assertEquals(['wbcreateclaim-create'], list(batch.tag_ids))

    def test_language_re(self):
        self.assertEquals('ru', language_re.match('/* wbsetlabel-add:1|ru */ Eupelops brevicuspis').group(1))

    def test_tags_with_languages(self):
        Edit.ingest_jsonlines('store/testdata/qs_batch_with_terms.json')
        batch = Batch.objects.get()
        self.assertEquals(['wbsetdescription-add', 'lang-eu'], list(batch.tag_ids))
        lang_tag = batch.tags.order_by('priority')[0]
        self.assertEquals('eu', lang_tag.display_name)

    def test_deletion_batch(self):
        Edit.ingest_jsonlines('store/testdata/deletion_edit.json')
        self.assertEquals(1, Batch.objects.count())
        batch = Batch.objects.get()
        self.assertEquals(['delete'], list(batch.tag_ids))


