from django.conf import settings
from django.db import models
from django.db import transaction
from django.db.utils import IntegrityError
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django_bulk_update.manager import BulkUpdateManager
from caching.base import CachingManager, CachingMixin
from collections import namedtuple
from cached_property import cached_property
from collections import defaultdict

import re
import json
from pytz import UTC
from datetime import datetime
from .utils import grouper

MAX_CHARFIELD_LENGTH = 190

class Tool(CachingMixin, models.Model):
    """
    A tool, making edits with some ids in the edit summaries
    """
    objects = CachingManager()

    Match = namedtuple('Match', 'uid user summary')

    name = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    shortid = models.CharField(max_length=32)

    idregex = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    idgroupid = models.IntegerField()

    summaryregex = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    summarygroupid = models.IntegerField()

    userregex = models.CharField(max_length=MAX_CHARFIELD_LENGTH, null=True, blank=True)
    usergroupid = models.IntegerField(null=True, blank=True)

    url = models.URLField()

    class Meta(object):
        base_manager_name = 'objects'

    def __str__(self):
        return self.name

    def match(self, user, comment):
        """
        Determines if an edit made with the supplied comment
        came from that tool, based on string matching with
        the supplied regular expressions.

        :returns: a Match named tuple if there
                is a match, None otherwise
        """
        idre = re.compile(self.idregex)
        idmatch = idre.match(comment)
        summaryre = re.compile(self.summaryregex)
        summarymatch = summaryre.match(comment)

        if not idmatch:
            return

        uid = idmatch.group(self.idgroupid)
        if not uid:
            return
        summary = ''
        if summarymatch:
            summary = summarymatch.group(self.summarygroupid)

        realuser = user
        if self.userregex:
            userre = re.compile(self.userregex)
            usermatch = userre.match(comment)
            if usermatch and usermatch.group(self.usergroupid):
                realuser = usermatch.group(self.usergroupid)

        return self.Match(uid=uid, user=realuser, summary=summary)

    @cached_property
    def nb_batches(self):
        return self.batch_set.count()

    @cached_property
    def nb_unique_users(self):
        return self.batch_set.values('user').distinct().count()

class BatchManager(BulkUpdateManager):
    """
    This makes Batch methods available in migrations.
    """
    use_in_migrations = True

class Batch(models.Model):
    """
    A group of edits
    """
    objects = BatchManager()

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    user = models.CharField(max_length=MAX_CHARFIELD_LENGTH, db_index=True, blank=False)
    uid = models.CharField(max_length=MAX_CHARFIELD_LENGTH, db_index=True, blank=False)

    summary = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    started = models.DateTimeField()
    ended = models.DateTimeField(db_index=True)
    nb_edits = models.IntegerField()
    nb_distinct_pages = models.IntegerField()
    nb_reverted_edits = models.IntegerField()
    nb_new_pages = models.IntegerField()
    total_diffsize = models.BigIntegerField()

    archived = models.BooleanField(default=False)

    # Internal field to keep track of when a batch was last modified.
    # In general this will not be equal to 'ended' as we can ingest
    # batches retrospectively after they ended.
    last_modified = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = (('tool','uid','user'))

    def __str__(self):
        return '<Batch {}:{} by {}>'.format(self.tool.shortid, self.uid, self.user)

    @property
    def full_uid(self):
        return self.tool.shortid+'/'+self.uid

    @property
    def editing_speed(self):
        time_diff = self.duration
        if time_diff <= 0:
            return '∞'
        return '{:5.1f}'.format((self.nb_edits * 60.)/time_diff).strip()

    @property
    def entities_speed(self):
        time_diff = self.duration
        if time_diff <= 0:
            return '∞'
        return '{:5.1f}'.format((self.nb_pages * 60.)/time_diff).strip()

    @cached_property
    def duration(self):
        return (self.ended - self.started).total_seconds()

    @property
    def nb_reverted(self):
        return self.nb_reverted_edits

    @cached_property
    def revertable_edits(self):
        return self.edits.filter(reverted=False)

    @cached_property
    def active_revert_task(self):
        try:
            return self.revert_tasks.filter(cancel=False,complete=False).get()
        except ObjectDoesNotExist:
            return None

    @property
    def can_be_reverted(self):
        return (self.nb_revertable_edits > 0 and
            self.active_revert_task is None and
            not self.archived)

    @cached_property
    def nb_revertable_edits(self):
        return self.nb_edits - self.nb_reverted_edits

    @cached_property
    def nb_pages(self):
        # used to be: self.edits.all().values('title').distinct().count()
        # but that is too expensive when the batches get large, so we cache this:
        return self.nb_distinct_pages

    @cached_property
    def nb_undeleted_new_pages(self):
        return self.revertable_edits.filter(changetype__in=['new','restore','delete','upload']).count()

    @property
    def nb_existing_pages(self):
        return self.nb_pages - self.nb_new_pages

    @property
    def avg_diffsize(self):
        if self.nb_edits:
            return self.total_diffsize / self.nb_edits
        return 0

    @property
    def url(self):
        return reverse('batch-view', args=[self.tool.shortid, self.uid])

    @property
    def csv_url(self):
        return reverse('csv-batch-edits', args=[self.tool.shortid, self.uid])

    @cached_property
    def tag_ids(self):
        return self.sorted_tags.values_list('id', flat=True)

    @cached_property
    def sorted_tags(self):
        return self.tags.order_by('-priority', 'id')

    @cached_property
    def reverting_batches(self):
        """
        Returns the list of batches which revert this batch
        """
        uids = self.revert_tasks.values_list('uid', flat=True)
        return Batch.objects.filter(uid__in=uids)

    @cached_property
    def reverted_batch(self):
        """
        Returns the batch reverted by this batch, if any (None otherwise).
        """
        try:
            return Batch.objects.get(revert_tasks__uid=self.uid)
        except Batch.DoesNotExist:
            return None

    def recompute_cached_stats(self):
        """
        Recomputes all the cached stats from the edits.
        This is expensive to do - it should only done if things have gone wrong.

        This does not save the Batch object yet.
        """
        # Refuse to do this if the batch is archived, as this will yield incorrect results
        if self.archived:
            return

        self.nb_edits = self.edits.count()
        self.nb_distinct_pages = self.edits.all().values('title').distinct().count()
        self.nb_reverted_edits = self.edits.all().filter(reverted=True).count()
        self.nb_new_pages = self.edits.all().filter(changetype='new').count()
        self.total_diffsize = self.edits.all().aggregate(total_diff=models.Sum('newlength')-models.Sum('oldlength')).get('total_diff')

    def archive(self, batch_inspector):
        """
        Recomputes all cached statistics from the edits, computes tags again,
        and then deletes all edits in the batch except the last few ones.

        This marks the batch as archived.
        """
        if self.archived:
            return

        # First, make sure we have up-to-date batch statistics and tags
        self.recompute_cached_stats()
        batch_inspector.add_missing_tags(self)

        # Then, archive the batch
        if self.nb_edits > settings.EDITS_KEPT_AFTER_ARCHIVAL:
            self.archived = True
            self.save()
            first_revid = self.edits.order_by('-newrevid')[settings.EDITS_KEPT_AFTER_ARCHIVAL-1].newrevid
            self.edits.filter(newrevid__lt=first_revid).delete()

    @classmethod
    def archive_old_batches(cls, batch_inspector):
        """
        Archive all batches which have not been modified for a long time
        and contain more edits than our archival threshold.

        This method is meant to be run periodically.
        """
        cutoff_date = datetime.utcnow().replace(tzinfo=UTC) - settings.BATCH_ARCHIVAL_DELAY
        for batch in cls.objects.filter(nb_edits__gt=settings.EDITS_KEPT_AFTER_ARCHIVAL, archived=False, ended__lt=cutoff_date):
            batch.archive(batch_inspector)

from tagging.models import Tag

class Edit(models.Model):
    """
    A MediaWiki edit as returned by the Event Stream API
    """
    id = models.BigIntegerField(unique=True, primary_key=True)
    oldrevid = models.BigIntegerField(null=True)
    newrevid = models.BigIntegerField()
    oldlength = models.IntegerField()
    newlength = models.IntegerField()
    timestamp = models.DateTimeField(db_index=True)
    title = models.CharField(max_length=MAX_CHARFIELD_LENGTH, db_index=True)
    namespace = models.IntegerField()
    uri = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    comment = models.TextField()
    parsedcomment = models.TextField()
    bot = models.BooleanField()
    minor = models.BooleanField()
    changetype = models.CharField(max_length=32)
    user = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    patrolled = models.BooleanField()

    # Inferred by us
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='edits')
    reverted = models.BooleanField(default=False)

    class Meta:
        indexes = [
            models.Index(fields=['batch', 'newrevid'])
        ]

    reverted_re = re.compile(r'^/\* undo:0\|\|(\d+)\|')

    @property
    def url(self):
        return '{}?diff={}&oldid={}'.format(settings.MEDIAWIKI_INDEX_ENDPOINT, self.newrevid, self.oldrevid)

    @property
    def revert_url(self):
        if self.oldrevid:
            return '{}?title={}&action=edit&undoafter={}&undo={}'.format(settings.MEDIAWIKI_INDEX_ENDPOINT, self.title, self.oldrevid, self.newrevid)
        elif self.changetype == 'delete':
            return '{}Special:Undelete/{}'.format(settings.MEDIAWIKI_BASE_URL, self.title)
        else:
            return '{}?title={}&action=delete'.format(settings.MEDIAWIKI_INDEX_ENDPOINT, self.title)

    def __str__(self):
        return '<Edit {} >'.format(self.url)

    @classmethod
    def from_json(cls, json_edit, batch):
        """
        Creates an edit from json, without saving it
        """
        # The following two fields are not provided in deletions
        revision = json_edit.get('revision', {})
        length = json_edit.get('length', {})
        changetype = json_edit['type']
        if changetype == 'log':
            changetype = json_edit['log_action']

        return cls(
            id = json_edit['id'],
            oldrevid = revision.get('old') or 0,
            newrevid = revision.get('new') or 0,
            oldlength = length.get('old') or 0,
            newlength = length.get('new') or 0,
            timestamp = datetime.fromtimestamp(json_edit['timestamp'], tz=UTC),
            title = json_edit['title'][:MAX_CHARFIELD_LENGTH],
            namespace = json_edit['namespace'],
            uri = json_edit['meta']['uri'][:MAX_CHARFIELD_LENGTH],
            comment = json_edit['comment'],
            parsedcomment = json_edit['parsedcomment'],
            bot = json_edit['bot'],
            minor = json_edit.get('minor') or False,
            changetype = changetype,
            user = json_edit['user'][:MAX_CHARFIELD_LENGTH],
            patrolled = json_edit.get('patrolled') or False,
            batch = batch,
            reverted = False)

    @classmethod
    def ingest_edits(cls, json_batch):
        # Map from (toolid, uid, user) to Batch object
        batches = {}
        model_edits = []
        reverted_ids = []
        deleted_pages = {} # map: title -> latest deletion timestamp
        restored_pages = {} # map: title -> latest restoration timestamp
        modified_pages = defaultdict(set) # map: batch_key -> set of touched pages
        new_tags = defaultdict(set)

        tools = Tool.objects.all()

        for edit_json in json_batch:
            if not edit_json or edit_json.get('namespace') not in settings.WATCHED_NAMESPACES:
                continue
            timestamp = datetime.fromtimestamp(edit_json['timestamp'], tz=UTC)

            # First, check if this is a revert
            revert_match = cls.reverted_re.match(edit_json['comment'])
            if revert_match:
                reverted_ids.append(int(revert_match.group(1)))

            # or a deletion
            if edit_json.get('log_action') == 'delete':
                deleted_pages[edit_json['title']] = timestamp

            # or a restore
            if edit_json.get('log_action') == 'restore':
                restored_pages[edit_json['title']] = timestamp

            # Then, try to match the edit with a tool
            match = None
            matching_tool = None
            for tool in tools:
                match = tool.match(edit_json['user'], edit_json['comment'])
                if match is not None:
                    matching_tool = tool
                    break

            if match is None:
                continue

            # Try to find an existing batch for that edit
            batch_key = (matching_tool.shortid, match.uid)
            batch = batches.get(batch_key)

            created = False
            if not batch:
                batch, created = Batch.objects.get_or_create(
                    tool=tool, uid=match.uid,
                    defaults={
                        'user': match.user[:MAX_CHARFIELD_LENGTH],
                        'summary': match.summary[:MAX_CHARFIELD_LENGTH],
                        'started': timestamp,
                        'ended': timestamp,
                        'nb_edits': 0,
                        'nb_distinct_pages': 0,
                        'nb_new_pages': 0,
                        'nb_reverted_edits': 0,
                        'total_diffsize': 0,
                    })

            # Check that the batch is owned by the right user
            if batch.user != match.user:
                if created:
                    batch.delete()
                continue

            batch.nb_edits += 1
            length_obj = edit_json.get('length') or {}
            batch.total_diffsize += (length_obj.get('new') or 0) - (length_obj.get('old') or 0)
            batch.ended = max(batch.ended, timestamp)

            batches[batch_key] = batch

            # Create the edit object
            model_edit = Edit.from_json(edit_json, batch)
            model_edits.append(model_edit)

            # Extract tags from the edit
            edit_tags = Tag.extract(model_edit)
            missing_tags = [tag.id for tag in edit_tags if tag.id not in batch.tag_ids]
            new_tags[batch.id].update(missing_tags)

            # Take note of the modified page, for computation of the number of entities edited by a batch
            modified_pages[batch_key].add(edit_json['title'])
            # And the number of new pages
            if model_edit.changetype == 'new':
                batch.nb_new_pages += 1

        # if we saw some deletions which match any creations or undeletions we know of, mark them as deleted.
        # We do this before creating the previous edits in the same batch, because deletions and restorations
        # do not come with unique ids to identify the creation, deletion or restoration that they undo
        # (this is a notion that we introduce ourselves) so if a deletion and the corresponding revert happen
        # in the same batch we need to inspect the order in which they happened.
        if deleted_pages:
            cls.mark_as_reverted(Edit.objects.filter(title__in=deleted_pages.keys(), changetype__in=['new','restore']))
            for edit in model_edits:
                if (edit.title in deleted_pages
                    and edit.changetype in ['new','restore']
                    and edit.timestamp < deleted_pages.get(edit.title)):
                    edit.reverted = True
                    edit.batch.nb_reverted_edits += 1
        # finally if we saw some undeletions which match any deletions we know of, mark them as undone
        if restored_pages:
            cls.mark_as_reverted(Edit.objects.filter(title__in=restored_pages.keys(), changetype='delete'))
            for edit in model_edits:
                if (edit.title in restored_pages
                    and edit.changetype == 'delete'
                    and edit.timestamp < restored_pages.get(edit.title)):
                    edit.reverted = True
                    edit.batch.nb_reverted_edits += 1

        # Create all Edit objects update all the batch objects
        if batches:
            # Update the number of modified pages
            for batch_key, pages in modified_pages.items():
                batch = batches.get(batch_key)
                existing_pages = set(batch.edits.filter(title__in=pages).values_list('title',flat=True))
                unseen_pages = pages-existing_pages
                batch.nb_distinct_pages += len(unseen_pages)

            # Create all the edit objects
            try:
                with transaction.atomic():
                    Edit.objects.bulk_create(model_edits)
            except IntegrityError as e:
                # Oops! Some of them existed already!
                # Let's add them one by one instead.
                for edit in model_edits:
                    try:
                        existing_edit = Edit.objects.get(id=edit.id)
                        # this edit was already seen: we need to remove it
                        # from the associated batch count
                        batch_key = (edit.batch.tool.shortid, edit.batch.uid)
                        batch = batches.get(batch_key)
                        if batch:
                            batch.nb_edits -= 1
                            batch.total_diffsize -= edit.newlength - edit.oldlength
                            if edit.changetype == 'new':
                                batch.nb_new_pages -= 1
                            if edit.reverted:
                                batch.nb_reverted_edits -= 1
                    except Edit.DoesNotExist:
                        edit.save()

            # update batch objects
            Batch.objects.bulk_update(list(batches.values()),
                update_fields=['ended', 'nb_edits', 'nb_distinct_pages',
                                'nb_reverted_edits', 'nb_new_pages', 'total_diffsize'])

            # update tags for batches
            if new_tags:
                Tag.add_tags_to_batches(new_tags)

        # If we saw any "undo" edit, mark all matching edits as reverted.
        # We do this after creating the latest edits because it could be possible that
        # an edit from the batch we just processed was undone in the same go.
        if reverted_ids:
            cls.mark_as_reverted(Edit.objects.filter(newrevid__in=reverted_ids))

    @classmethod
    def ingest_jsonlines(cls, fname, batch_size=50):

        def lines_generator():
            with open(fname, 'r') as f:
                for line in f:
                    try:
                        yield json.loads(line.strip())
                    except ValueError:
                        pass

        for batch in grouper(lines_generator(), batch_size, ):
            cls.ingest_edits(batch)

    @classmethod
    def mark_as_reverted(cls, qs):
        """
        Given a queryset of edits, mark each edit object as reverted and update
        the batch-level statistics accordingly.
        """
        nb_updated = qs.update(reverted=True)
        # there is probably a clever way to do this in SQL but there are generally
        # few reverts so this scales fine for now.
        if nb_updated:
            for edit in qs:
                b = edit.batch
                b.nb_reverted_edits += 1
                b.save(update_fields=['nb_reverted_edits'])

    @classmethod
    def latest_edit_time(cls):
        try:
            return Edit.objects.all().order_by('-timestamp').values_list('timestamp', flat=True)[0]
        except IndexError: # no edit in the database…
            return datetime.utcnow().replace(tzinfo=UTC)

    @classmethod
    def current_lag(cls):
        """
        Returns the amount of time since the last edit successfully ingested.
        """
        return datetime.utcnow().replace(tzinfo=UTC) - cls.latest_edit_time()
