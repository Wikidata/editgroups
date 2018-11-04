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
        summary = ''
        if summarymatch:
            summary = summarymatch.group(self.summarygroupid)

        realuser = user
        if self.userregex:
            userre = re.compile(self.userregex)
            usermatch = userre.match(comment)
            if usermatch:
                realuser = usermatch.group(self.usergroupid)

        return self.Match(uid=uid, user=realuser, summary=summary)


class Batch(models.Model):
    """
    A group of edits
    """
    objects = BulkUpdateManager()

    tool = models.ForeignKey(Tool, on_delete=models.CASCADE)
    user = models.CharField(max_length=MAX_CHARFIELD_LENGTH, db_index=True)
    uid = models.CharField(max_length=MAX_CHARFIELD_LENGTH, db_index=True)

    summary = models.CharField(max_length=MAX_CHARFIELD_LENGTH)
    started = models.DateTimeField()
    ended = models.DateTimeField(db_index=True)
    nb_edits = models.IntegerField()

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
        return self.edits.filter(reverted=True).count()

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
            self.active_revert_task is None)

    @cached_property
    def nb_revertable_edits(self):
        return self.revertable_edits.count()

    @cached_property
    def nb_pages(self):
        return self.edits.all().values('title').distinct().count()

    @cached_property
    def nb_new_pages(self):
        return self.edits.all().filter(changetype='new').count()

    @cached_property
    def nb_undeleted_new_pages(self):
        return self.revertable_edits.filter(changetype__in=['new','restore','delete']).count()

    @property
    def nb_existing_pages(self):
        return self.nb_pages - self.nb_new_pages

    @property
    def avg_diffsize(self):
        return self.edits.all().aggregate(avg_diff=models.Avg('newlength')-models.Avg('oldlength')).get('avg_diff')

    @property
    def url(self):
        return reverse('batch-view', args=[self.tool.shortid, self.uid])

    @cached_property
    def tag_ids(self):
        return self.sorted_tags.values_list('id', flat=True)

    @cached_property
    def sorted_tags(self):
        return self.tags.order_by('-priority', 'id')

from tagging.models import Tag

class Edit(models.Model):
    """
    A wikidata edit as returned by the Event Stream API
    """
    id = models.IntegerField(unique=True, primary_key=True)
    oldrevid = models.IntegerField(null=True)
    newrevid = models.IntegerField(db_index=True)
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

    reverted_re = re.compile(r'^/\* undo:0\|\|(\d+)\|')

    @property
    def url(self):
        return 'https://www.wikidata.org/wiki/index.php?diff={}&oldid={}'.format(self.newrevid,self.oldrevid)

    @property
    def revert_url(self):
        if self.oldrevid:
            return 'https://www.wikidata.org/w/index.php?title={}&action=edit&undoafter={}&undo={}'.format(self.title, self.oldrevid, self.newrevid)
        elif self.changetype == 'delete':
            return 'https://www.wikidata.org/wiki/Special:Undelete/{}'.format(self.title)
        else:
            return 'https://www.wikidata.org/w/index.php?title={}&action=delete'.format(self.title)

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
        new_tags = defaultdict(set)

        tools = Tool.objects.all()

        for edit_json in json_batch:
            if not edit_json or edit_json.get('namespace') not in [0,120]:
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
                        'user': match.user,
                        'summary': match.summary,
                        'started': timestamp,
                        'ended': timestamp,
                        'nb_edits': 0,
                    })

            # Check that the batch is owned by the right user
            if batch.user != match.user:
                if created:
                    batch.delete()
                continue

            batch.nb_edits += 1
            batch.ended = max(batch.ended, timestamp)

            batches[batch_key] = batch

            # Create the edit object
            model_edit = Edit.from_json(edit_json, batch)
            model_edits.append(model_edit)

            # Extract tags from the edit
            edit_tags = Tag.extract(model_edit)
            missing_tags = [tag.id for tag in edit_tags if tag.id not in batch.tag_ids]
            new_tags[batch.id].update(missing_tags)

        # if we saw some deletions which match any creations or undeletions we know of, mark them as deleted.
        # We do this before creating the previous edits in the same batch, because deletions and restorations
        # do not come with unique ids to identify the creation, deletion or restoration that they undo
        # (this is a notion that we introduce ourselves) so if a deletion and the corresponding revert happen
        # in the same batch we need to inspect the order in which they happened.
        if deleted_pages:
            Edit.objects.filter(title__in=deleted_pages.keys(), changetype__in=['new','restore']).update(reverted=True)
            for edit in model_edits:
                if (edit.title in deleted_pages
                    and edit.changetype in ['new','restore']
                    and edit.timestamp < deleted_pages.get(edit.title)):
                    edit.reverted = True
        # finally if we saw some undeletions which match any deletions we know of, mark them as undone
        if restored_pages:
            Edit.objects.filter(title__in=restored_pages.keys(), changetype='delete').update(reverted=True)
            for edit in model_edits:
                if (edit.title in restored_pages
                    and edit.changetype == 'delete'
                    and edit.timestamp < restored_pages.get(edit.title)):
                    edit.reverted = True

        # Create all Edit objects update all the batch objects
        if batches:
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
                    except Edit.DoesNotExist:
                        edit.save()

            # update batch objects
            Batch.objects.bulk_update(list(batches.values()), update_fields=['ended', 'nb_edits'])

            # update tags for batches
            if new_tags:
                Tag.add_tags_to_batches(new_tags)

        # If we saw any "undo" edit, mark all matching edits as reverted.
        # We do this after creating the latest edits because it could be possible that
        # an edit from the batch we just processed was undone in the same go.
        if reverted_ids:
            Edit.objects.filter(newrevid__in=reverted_ids).update(reverted=True)

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
