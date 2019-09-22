.. _page-tagging:

Batch archival
==============

EditGroups stores a copy of the edit metadata, for each edit tracked by the tool.
As times goes by, this means maintaining a fairly large database, with an edit table
with hundreds of millions of rows.

Since the purpose of EditGroups is primarily to provide a view on batches (rather 
than individual edits), we do not actually need to store all these edits for ever.
Once a batch is old enough, the chances that anyone will want to undo it are low
(since its changes will be burried deep in the history and many will not be allowed
to be undone by Wikibase).

Batch archival consists in deleting edits from the database for old batches. This
is configurable using the following settings:

- ``BATCH_ARCHIVAL_DELAY``: amount of time after which batches should be archived (one year by default);
- ``EDITS_KEPT_AFTER_ARCHIVAL``: number of edits to keep in each archived batch. This is intended to help get a sense of what the batch does even after archival (10 by default);
- ``BATCH_ARCHIVAL_PERIODICITY``: how often should we check for old batches and archive them (daily by default).

Once a batch is archived, it can no longer be undone.
