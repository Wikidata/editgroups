.. _page-reverting:

Reverting batches
=================

Reverting a batch is a long-running operation. Therefore it cannot be run during the course
of answering an HTTP request: it is delegated to the Celery tasks backend. This makes it possible
for users to close their browser without stopping the revert process.

Detection of reverted edits
---------------------------

EditGroups can detect when an edit is undone, and counts the number of reverted edits in each batch.
This is useful to detect problematic batches: if many edits in a batch have been undone manually by
users, there might be a systemic issue in the batch and it should perhaps be undone entirely.
This data is also used when reverting batches from EditGroups directly, so that the reverting process
only attempts to undo edits that have not been undone yet.

The detection of a revert is done by scanning all ``undo`` edits made, and matching the revision ids
present in the summary with those stored in the database. Therefore, edits done using the ``restore``
or ``rollback`` functionalities are not taken into account so far. Furthermore, manual reverts (such as
deleting a claim added by a previous edit) are not recorded either.

When reverting fails
--------------------

When running a revert batch from EditGroups, undoing some of the edits can fail. This can happen when
the edit was already undone by means that are not tracked by EditGroups (see above) or when conflicting
edits have been added on top of the original edit.

In this case, the revert batch continues and tries to revert the other edits. The reason for this design
choice is that a reverting failure generally means that the problem with the edit has been corrected manually
already.

Rights required for reverting
-----------------------------

Administrative rights are required to undo edits with entity creations, entity deletions or restoring deleted entities.
Therefore, EditGroups forbids reverting any batch containing those actions to non-administrators, even if some of the
edits could be reverted anyway. This design choice is to prevent batches from being half-reverted, with new entities
being left over, unlinked to the rest of the wiki.

Potential improvements
----------------------

It could be useful to be able to revert only a selection of edits in a batch, on the basis of some criterion
(such as the use of a particular action, or using a SPARQL query to select a subset of items where reverts should happen).
Any contribution towards this will be most welcome.
