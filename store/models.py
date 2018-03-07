from django.db import models
from django.urls import reverse
from django_bulk_update.manager import BulkUpdateManager
from collections import namedtuple

import re
import json
from pytz import UTC
from datetime import datetime
from .utils import grouper

class Tool(models.Model):
    """
    A tool, making edits with some ids in the edit summaries
    """
    Match = namedtuple('Match', 'uid user summary')

    name = models.CharField(max_length=256)
    shortid = models.CharField(max_length=32)

    idregex = models.CharField(max_length=512)
    idgroupid = models.IntegerField()

    summaryregex = models.CharField(max_length=512)
    summarygroupid = models.IntegerField()

    userregex = models.CharField(max_length=512, null=True)
    usergroupid = models.IntegerField(null=True)

    url = models.URLField()

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

        if not idmatch or not summarymatch:
            return

        uid = idmatch.group(self.idgroupid)
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
    user = models.CharField(max_length=512, db_index=True)
    uid = models.CharField(max_length=128, db_index=True)

    summary = models.CharField(max_length=512)
    started = models.DateTimeField()
    ended = models.DateTimeField()
    nb_edits = models.IntegerField()

    class Meta:
        unique_together = (('user','tool','uid'))

    def __str__(self):
        return '<Batch {}:{} by {}>'.format(self.tool.shortid, self.uid, self.user)

    @property
    def url(self):
        return reverse('batch-view', args=[self.tool.shortid, self.uid])


class Edit(models.Model):
    """
    A wikidata edit as returned by the Event Stream API
    """
    id = models.IntegerField(unique=True, primary_key=True)
    oldrevid = models.IntegerField(null=True)
    newrevid = models.IntegerField()
    oldlength = models.IntegerField()
    newlength = models.IntegerField()
    timestamp = models.DateTimeField()
    title = models.CharField(max_length=256)
    namespace = models.IntegerField()
    uri = models.CharField(max_length=512)
    comment = models.CharField(max_length=500)
    parsedcomment = models.CharField(max_length=1000)
    bot = models.BooleanField()
    minor = models.BooleanField()
    changetype = models.CharField(max_length=32)
    user = models.CharField(max_length=256)
    patrolled = models.BooleanField()

    # Inferred by us
    batch = models.ForeignKey(Batch, on_delete=models.CASCADE, related_name='edits')
    reverted = models.BooleanField(default=False)

    @property
    def url(self):
        return 'https://www.wikidata.org/wiki/index.php?diff={}&oldid={}'.format(self.newrevid,self.oldrevid)

    def __str__(self):
        return '<Edit {} >'.format(self.url)

    @classmethod
    def from_json(cls, json_edit, batch):
        """
        Creates an edit from json, without saving it
        """
        return cls(
            id = json_edit['id'],
            oldrevid = json_edit['revision']['old'],
            newrevid = json_edit['revision']['new'],
            oldlength = json_edit['length']['old'],
            newlength = json_edit['length']['new'],
            timestamp = datetime.fromtimestamp(json_edit['timestamp'], tz=UTC),
            title = json_edit['title'][:256],
            namespace = json_edit['namespace'],
            uri = json_edit['meta']['uri'][:512],
            comment = json_edit['comment'][:500],
            parsedcomment = json_edit['parsedcomment'][:1000],
            bot = json_edit['bot'],
            minor = json_edit['minor'],
            changetype = json_edit['type'],
            user = json_edit['user'][:256],
            patrolled = json_edit['patrolled'],
            batch = batch,
            reverted = False)


    @classmethod
    def ingest_edits(cls, json_batch):
        # Map from (toolid, uid, user) to Batch object
        batches = {}
        model_edits = []

        tools = Tool.objects.all()

        for edit_json in json_batch:
            if not edit_json:
                continue
            timestamp = datetime.fromtimestamp(edit_json['timestamp'], tz=UTC)

            # Try to match the edit with a tool
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
            batch_key = (matching_tool.shortid, match.uid, match.user)
            batch = batches.get(batch_key)

            if not batch:
                batch, created = Batch.objects.get_or_create(
                    tool=tool, user=match.user, uid=match.uid,
                    defaults={
                        'summary': match.summary,
                        'started': timestamp,
                        'ended': timestamp,
                        'nb_edits': 0,
                    })

            batch.nb_edits += 1
            batch.ended = max(batch.ended, timestamp)

            batches[batch_key] = batch

            # Create the edit object
            model_edits.append(Edit.from_json(edit_json, batch))

        # Update all the batch objects
        if batches:
            Batch.objects.bulk_update(list(batches.values()), update_fields=['ended', 'nb_edits'])

            # Create all the edit objects
            Edit.objects.bulk_create(model_edits)

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

