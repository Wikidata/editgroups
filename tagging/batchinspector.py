
from django.db.models import Q
from time import sleep

from .newentityinspector import NewEntityInspector
from .diffinspector import DiffInspector
from .diffdigest import DiffDigest
from .models import Tag

from store.models import Batch

class BatchInspector(object):
    """
    Extracts tags from diffs and revision ids,
    when the batch contains actions that do not
    expose enough information in their summaries.
    """

    tags_for_diff_inspection = {
        'wbeditentity-update',
        'wbeditentity-update-languages',
        'wbeditentity-update-languages-and-other',
        'wbcreateclaim', # for qualifiers
        # 'wbsetclaim-update', # could add qualifiers, but currently only used by OR to add refs
    }

    max_edits_fetch = 50 # only look for that many edits with inspectable actions
    max_diff_inspections = 10 # one request for each
    max_new_items_inspections = 25 # one request for all, cheaper

    requests_delay = 0.5

    def __init__(self, new_entity_inspector=None, diff_inspector=None):
        self.new_entity_inspector = new_entity_inspector or NewEntityInspector()
        self.diff_inspector = diff_inspector or DiffInspector()

    def inspect(self, batch):
        """
        Inspect the given batch if needed, and add the corresponding
        tags to the batch.
        """
        digest = DiffDigest()
        tags = set(batch.tag_ids)

        if tags & self.tags_for_diff_inspection:
            # We need to inspect some diffs!
            edits = batch.edits.filter(oldrevid__gt=0)[:self.max_edits_fetch]
            nb_edits_inspected = 0
            for edit in edits:
                if set(tag.id for tag in Tag.extract(edit)) & self.tags_for_diff_inspection:
                    digest += self.diff_inspector.inspect(edit.oldrevid, edit.newrevid)
                    nb_edits_inspected += 1
                    sleep(self.requests_delay)
                if nb_edits_inspected >= self.max_diff_inspections:
                    break

        if batch.nb_new_pages:
            # We need to inspect some new items!
            revids = batch.edits.filter(oldrevid=0)[:self.max_new_items_inspections].values_list('newrevid', flat=True)
            digest += self.new_entity_inspector.inspect(revids)
            sleep(self.requests_delay)

        return digest

    def add_missing_tags(self, batch):
        """
        Like `inspect`, but adds any missing tags to the batch instead of returning a digest.
        """
        diffdigest = self.inspect(batch)
        tags = ([Tag.for_property(pid) for pid in diffdigest.statements | diffdigest.qualifiers ] +
                [Tag.for_language(lang) for lang in diffdigest.labels | diffdigest.descriptions | diffdigest.aliases | diffdigest.sitelinks ])
        tags_not_there_yet = [tag for tag in tags if tag.id not in batch.tag_ids]
        Tag.add_tags_to_batches({batch.id: [tag.id for tag in tags_not_there_yet]})

    def inspect_batches_since(self, since_time):
        """
        Inspects all batches that need inspection, only considering
        batches modified since the given time.
        """
        queryset = Batch.objects.filter(Q(tags__id__in = self.tags_for_diff_inspection) | Q(nb_new_pages__gt = 0), last_modified__gt=since_time, archived=False).order_by('ended').distinct()
        for batch in queryset:
            self.add_missing_tags(batch)

