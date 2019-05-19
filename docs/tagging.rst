.. _page-tagging:

Batch tagging
=============

EditGroups tries to provide as much metadata as possible for each batch.
The goal is to make them more findable, make it possible to spot potential issues
without having to review individual edits, and potentially to provide useful analytics
for administrators, researchers and anyone interested in studying bot activity.

Beyond the basic statistics such as the number of edits or the number of new entities created,
EditGroups adds a notion of "tags" to groups. These tags are different from MediaWiki's tags, which
are applied on each edit individually.

Possible tags
-------------

Each tag is identified by a string identifier, such as ``lang-de``.
We currently store three sorts of tags on batches:

- **action** tags, which indicate which sort of edit was made (adding a claim, adding a reference, removing a description, and so on). These action tags correspond to API actions as exposed in the edit summary of the edits involved. The Wikibase API provide various methods, some of which overlap in functionality: for instance, adding a claim can be recorded either as ``wbcreateclaim-create`` or ``wbsetclaim-create`` depending on whether the `wbcreateclaim <https://www.wikidata.org/w/api.php?action=help&modules=wbcreateclaim>`_ or `wbsetclaim <https://www.wikidata.org/w/api.php?action=help&modules=wbsetclaim>`_ API actions were used.
- **language** tags, which are prefixed by ``lang-``. These tags are added when the batch changes terms (labels, descriptions or aliases) in the corresponding language. The code following the ``lang-`` prefix is a Wikimedia language code, such as ``lang-de``.
- **property** tags, which are prefixed by ``prop-``. These tags are added when the batch adds claims or qualifiers with the given property. The code following the ``prop-`` prefix is the property id, such as ``prop-P2427``.
 
How tags are computed
---------------------

Tags are aggregated from edits into batches, and various strategies are used to make this annotation scalable.

First, the edit summary of each edit provides some information about the edit: it always contains the code of the API action used, 
and often it also indicates a language or property id used in the edit. For instance::

    /* wbsetlabel-add:1|ro */ Planodema nigra, #quickstatements; [[:toollabs:quickstatements/#/batch/9435|batch #9435]] by [[User:KlaudiuMihaila|]]

indicates that a Romanian label was changed, and for this action we know that the edit did not impact anything else on the item. We can therefore extract the action and language code from this summary using regular expressions.

However, not all actions are transparent like this one.
Entity creations can add arbitrary content in a single edit, and other changes can be performed with the ``wbeditentity`` action.
These actions do not expose any of the content added or removed in the edit summary.
In the interest of making batches using these actions less opaque, EditGroups has an additional edit inspection feature
which retrieves the revisions (in the case of a creation) or diffs (in the case of a modification) of a sample of these opaque edits
for each batch. Not all opaque edits are inspected, as we assume that a batch will generally do the same sort of change on many items, and try to reduce the API usage to a minimum.

This batch inspection is run as a periodic task in Celery, which inspects the latest active batches with opaque actions and adds
any missing tag to them.
Therefore, it is possible that tags are not complete for a given batch, if a language or property is only used in edits that were 
not inspected. Fresh edit groups with opaque actions also stay untagged for a while, before the periodic task kicks in. The reason for running this inspection as a periodic task rather than in the main edit ingestion routine is to make sure we do not
weaken the edit ingestion itself, by adding calls to an API which can fail or be slow to respond.
Suggestions of other architectures are of course most welcome.

