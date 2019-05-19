.. _page-api:

EditGroups' API
===============

EditGroups offers a web API that can be used to search for edit groups and retrieve
statistics about them.

Accessing the API
-----------------

Thanks to the `Django REST framework <https://www.django-rest-framework.org/>`_, the API and the web UI 
have been designed and implemented in the same go. This means they work in the same way: every HTML page
in EditGroups has a machine-readable counterpart. This can be accessed either by prepending ``/api/`` to
the URL, or by using `content negociation <https://en.wikipedia.org/wiki/Content_negotiation>`_.

For instance, the page `https://tools.wmflabs.org/editgroups/b/OR/cf1b2a01a/ <https://tools.wmflabs.org/editgroups/b/OR/cf1b2a01a/>`_
can be obtained in a JSON format at `https://tools.wmflabs.org/editgroups/api/b/OR/cf1b2a01a/ <https://tools.wmflabs.org/editgroups/b/OR/cf1b2a01a/>`_, or by adding the appropriate header::

    curl -H "Accept: application/json" https://tools.wmflabs.org/editgroups/b/OR/cf1b2a01a/

Each API endpoint supports the same parameters as its HTML counterpart. For instance, the main page
lists the most recent edit groups and can be accessed as an API as well, at https://tools.wmflabs.org/editgroups/api/.

When viewing API pages in a browser, Django Rest Framework automatically adds an HTML wrapper around the API output.
When querying the same URI in a script, only the JSON API output will be required (no ``Accept`` header required).

Reverting batches via the API
-----------------------------

To revert batches through EditGroups, you will need to login to EditGroups via OAuth and store the corresponding 
authentication cookies. Reverting itself is done by posting a POST request to the ``/undo/start/`` subpage of a batch
page, such as ``https://tools.wmflabs.org/editgroups/b/OR/cf1b2a01a/undo/start/``, with the ``comment`` parameter
to indicate an edit summary for the reverting group.

