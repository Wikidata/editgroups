.. _page-other_wiki:

Running on other wikis
======================

EditGroups is originally designed for Wikidata but could be run on other Wikibase or even MediaWiki instances.
Some lightweight modifications to the code will be required. Any contribution towards this goal will be gratefully received.

Changes required
----------------

* Making mentions of Wikidata and its API depend on configuration parameters that can be changed in the settings;
* Allowing the ingestion of edits by polling the RecentChanges feed instead of using the Wikimedia EventStream;
* Making the user groups required to undo configurable.

Configuration of the tools
--------------------------

The regular expressions used to detect batch identifiers and tools in edits are considered user data
and are therefore stored in their own SQL table. They can be configured from EditGroups' admin interface
(which uses Django's standard admin functionality), available on the canonical instance at https://tools.wmflabs.org/editgroups/admin/.

To access this interface, you need to create an administrator account in EditGroups using the ``python manage.py createsuperuser`` command. Being an administrator on the target wiki does not automatically grant you rights to administer EditGroups.

