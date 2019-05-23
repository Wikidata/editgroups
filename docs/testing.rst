.. _page-testing:

Testing
=======

EditGroups comes with an extensive test suite, that can be run using Django's testing tools: ``python manage.py test``.
This will create a test database, so that the changes made do not interfere with any production database.

We encourage any prospective contributors to embrace a test-driven development approach and write tests for as many
scenarios as possible. Contributions without tests are still gratefully received.

Getting test data
-----------------

Many tests load their test data using the ``Edit.ingest_jsonlines`` method, which loads a set of edits
from their JSON representation as exposed by the EventStream. You can obtain such representation by dumping
the EventStream using the ``dump_events.py`` script at the root of the repository::

    python dump_events.py > my_event_dump.json

If you do some test edits on Wikidata while this script is running, this will record your edits in the JSON
file. You can then rework this file manually if needed, to generate the test scenario you need.

