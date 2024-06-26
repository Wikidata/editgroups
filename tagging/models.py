from django.db import models

from caching.base import CachingManager, CachingMixin
from django.utils.translation import gettext_lazy as _
from store.models import Batch
from collections import defaultdict

import re

# These tags can be extracted from the lib/i18n/en.json file in Wikibase,
# and other files from extensions (such as lexeme)
tag_to_readable_name = {
	"wbsetitem": _("new items"),
	"wbcreate-new": _("new entities"),
	"wbcreateredirect": _("new redirects"),
	"wbeditentity": _("new entities"),
	"wbeditentity-create": _("new entities"),
        "wbeditentity-update": _("edits entities"),
	"wbeditentity-override": _("clears entities"),
	"wbsetreference": _("sets references"),
	"wbsetreference-add": _("adds references"),
	"wbsetreference-set": _("changes references"),
	"wbsetlabel-add": _("adds labels"),
	"wbsetlabel-set": _("changes labels"),
	"wbsetlabel-remove": _("removes labels"),
	"wbsetdescription-add": _("adds descriptions"),
	"wbsetdescription-set": _("changes descriptions"),
	"wbsetdescription-remove": _("removes descriptions"),
	"wbsetaliases-set": _("sets aliases"),
	"wbsetaliases-add-remove": _("sets aliases"),
	"wbsetaliases-add": _("sets aliases"),
	"wbsetaliases-remove": _("removes aliases"),
	"wbsetaliases-update": _("changes aliases"),
	"wbsetlabeldescriptionaliases": _("changes terms"),
	"wbsetsitelink-add": _("adds sitelinks"),
	"wbsetsitelink-add-both": _("adds sitelinks and badges"),
	"wbsetsitelink-set": _("changes sitelinks"),
	"wbsetsitelink-set-badges": _("changes badges"),
	"wbsetsitelink-set-both": _("changes sitelinks and badges"),
	"wbsetsitelink-remove": _("removes sitelinks"),
	"wblinktitles-create": _("new entities"),
	"wblinktitles-connect": _("adds sitelinks"),
	"wbcreateclaim-value": _("adds claims"),
	"wbcreateclaim-novalue": _("new novalue claims"),
	"wbcreateclaim-somevalue": _("new somevalue claims"),
	"wbcreateclaim": _("adds claims"),
	"wbsetclaimvalue": _("changes claim values"),
	"wbremoveclaims": _("removes claims"),
	"wbremoveclaims-remove": _("removes claims"),
	"wbremoveclaims-update": _("removes claims"),
	"special-create-item": _("new items"),
	"wbcreateclaim-create": _("adds claims"),
	"wbsetclaim-update": _("changes claims"),
	"wbsetclaim-create": _("adds claims"),
	"wbsetclaim-update-qualifiers": _("changes qualifiers"),
	"wbsetclaim-update-references": _("changes references"),
	"wbsetclaim-update-rank": _("changes ranks"),
	"clientsitelink-update": _("sitelinks moved"),
	"clientsitelink-remove": _("sitelinks deleted"),
	"wbsetqualifier-add": _("adds qualifiers"),
	"wbsetqualifier-update": _("changes qualifiers"),
	"wbremovequalifiers-remove": _("removes qualifiers"),
	"wbremovereferences-remove": _("removes references"),
	"wbmergeitems-from": _("merges items"),
	"wbmergeitems-to": _("merges items"),
	"wbcreate-new": _("new items"),
	"wbeditentity": _("new items"),
	"wbeditentity-create-item": _("new items"),
	"wbeditentity-create-property": _("new properties"),
	"wbeditentity-override": _("clears items"),
        "wbeditentity-update-languages": _("updates terms"),
        "wbeditentity-update-languages-short": _("updates terms"),
        "wbeditentity-update-languages-and-other": _("updates terms and statements"),
        "wbeditentity-update-languages-and-other-short": _("updates terms and statements"),
	"wblinktitles-create": _("clears items"),
	"wblinktitles-connect": _("new sitelinks"),
	"wbcreate-new": _("new items"),
	"wbeditentity-override": _("clears items"),
	"special-create-property": _("new properties"),
        "undo": _("undo edits"),
        "delete": _("delete items"),
        "restore": _("restore items"),
	"wbeditentity-create-lexeme": _("new lexemes"),
	"wbeditentity-create-form": _("new forms"),
	"wbeditentity-create-sense": _("new senses"),
        "add-form": _("adds forms"),
        "remove-form": _("removes forms"),
        "update-form-representations": _("updates form representations"),
        "add-form-representations": _("adds form representations"),
        "set-form-representations": _("changes form representations"),
        "remove-form-representations": _("removes form representations"),
        "update-form-grammatical-features": _("updates grammatical features"),
        "add-form-grammatical-features": _("adds grammatical features"),
        "remove-form-grammatical-features": _("removes grammatical features"),
        "update-form-elements": _("updates forms"),
        "add-sense": _("adds senses"),
        "remove-sense": _("removes senses"),
        "update-sense-glosses": _("updates glosses"),
        "add-sense-glosses": _("adds glosses"),
        "set-sense-glosses": _("changes glosses"),
        "remove-sense-glosses": _("removes glosses"),
        "update-sense-elements": _("changes glosses"),
    "upload": _("uploads files"),

}

action_re = re.compile('^/\* ([a-z\-]*):.*')
language_re = re.compile('^/\* wb[a-z\-]*:\d+\|([a-z\-]+) \*/')
property_re = re.compile('^/\* wb[a-z\-]*:[\d\|]* \*/ \[\[Property:(P[1-9]\d+)\]\]: ')

class TagManager(CachingManager):
    """
    This enables methods in data migrations.
    """
    use_in_migrations = True

class Tag(CachingMixin, models.Model):
    """
    A tag, which represents a feature extracted from an edit
    and aggregated at the level of batches.
    """
    objects = TagManager()

    #: The content of the tag
    id = models.CharField(max_length=128, primary_key=True)
    #: Introduces an ordering on tags, so that the most important get displayed first
    priority = models.IntegerField(default=0)
    #: The batches that are tagged with this tag.
    batches = models.ManyToManyField(Batch, related_name='tags')
    #: Color for the tag (HTML coded, including hash)
    color = models.CharField(max_length=32, default='#939393')

    @property
    def display_name(self):
        """
        Returns the text to display in the tag.
        It can return None, in which case the tag should not be displayed.
        """
        if self.id in tag_to_readable_name:
            return tag_to_readable_name[self.id]
        else:
            return self.code

    @property
    def category(self):
        """
        Returns the type of tag (action, lang or prop)
        """
        if self.id in tag_to_readable_name:
            return 'action'
        elif self.id.startswith('lang-'):
            return 'lang'
        elif self.id.startswith('prop-'):
            return 'prop'
        return 'no category for '+self.id

    @property
    def code(self):
        """
        Returns the property id or language code if the
        tag is of these types.
        """
        if self.id.startswith('lang-'):
            return self.id[len('lang-'):]
        elif self.id.startswith('prop-'):
            return self.id[len('prop-'):]

    @classmethod
    def add_tags_to_batches(cls, batch_to_tags):
        """
        Efficiently adds tags to batches (in one query).

        This method requires that the batches have not been tagged yet with the list of tag
        names supplied.

        :param batch_to_tags: a dictionnary from batch ids to the new tag ids they should have.
        """
        ThroughModel = cls.batches.through

        instances = []
        for batch_id, tags in batch_to_tags.items():
            for tag in tags:
                instances.append(ThroughModel(tag_id=tag, batch_id=batch_id))

        ThroughModel.objects.bulk_create(instances)

    @classmethod
    def extract(cls, edit):
        """
        Extracts tags from an edit, without saving the relations
        to the batch yet (this can be done all at once for many edits
        later on).
        :returns: a list of tags
        """
        # Extract action types
        action_match = action_re.match(edit.comment)
        if action_match:
            yield cls.for_action(action_match.group(1))

        # Extract properties
        property_match = property_re.match(edit.comment)
        if property_match:
            yield cls.for_property(property_match.group(1))

        # Extract languages
        language_match = language_re.match(edit.comment)
        if language_match:
            yield cls.for_language(language_match.group(1))

        # Other actions
        if edit.changetype in tag_to_readable_name:
            yield cls.for_changetype(edit.changetype)


    @classmethod
    def for_action(cls, action):
        """
        Returns a tag for a given action type.
        """
        tag_name = action
        tag, created = cls.objects.get_or_create(id=tag_name,
            defaults={'priority': 10})
        return tag

    @classmethod
    def for_property(cls, pid):
        """
        Returns a tag for a given property id.
        """
        tag_name = 'prop-'+pid
        tag, created = cls.objects.get_or_create(id=tag_name,
            defaults={'priority':2, 'color': '#5180bc'})
        return tag

    @classmethod
    def for_language(cls, lang):
        """
        Returns a tag for a given language code.
        """
        tag_name = 'lang-'+lang
        tag, created = cls.objects.get_or_create(id=tag_name,
            defaults={'priority':5, 'color':'#3eabab'})
        return tag

    @classmethod
    def for_changetype(cls, changetype):
        """
        Returns a tag for a given change type.
        """
        tag, created = cls.objects.get_or_create(id=changetype,
            defaults={'priority':20, 'color':'#dc4ec9'})
        return tag

    @classmethod
    def retag_all_batches(cls):
        """
        Useful to retag all batches after creating new tags.
        Existing tags should be cleared first.
        """
        from store.models import Edit
        cls.retag_edits(Edit.objects.all().iterator())

    @classmethod
    def retag_edits(cls, edits):
        """
        Useful to retag all batches after creating new tags.
        Existing tags should be cleared first.
        """
        batch_to_tags = defaultdict(set)
        for edit in edits:
            tags = cls.extract(edit)
            missing_tags = [t for t in tags if t.id not in edit.batch.tag_ids]
            batch_to_tags[edit.batch_id].update(missing_tags)

        ThroughModel = cls.batches.through
        instances = []
        for batch_id, tags in batch_to_tags.items():
            for tag in tags:
                instances.append(ThroughModel(batch_id=batch_id,tag_id=tag.id))

        ThroughModel.objects.bulk_create(instances)
