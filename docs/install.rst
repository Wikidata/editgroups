.. _page-install:

Deploying
=========

Overview of the requirements
----------------------------

EditGroups is a `Django <https://www.djangoproject.com/start/overview/>`_ app, it therefore follows the `guidelines about deployment
for Django projects <https://docs.djangoproject.com/en/2.2/howto/deployment/>`_. To run asynchronous tasks, such as reverting edit groups, it uses
`Celery <http://www.celeryproject.org/>`_, a tasks backend commonly used in conjunction with Django.

To run it, you will need:

- a web server with WSGI support, to deploy the Django app;
- a SQL server supported by Django, such as MySQL, PostgreSQL or MariaDB;
- Python 3 and dependencies listed in the ``requirements.txt`` file (these should be installed in a virtualenv, see below);
- a redis server, which will be used for communication between the web server and the tasks backend.

Running locally
---------------

When working on EditGroups, you can run it locally.
First, configure your database and redis by copying the ``editgroups/settings/secret_template.py`` to
``editgroups/settings/secret.py`` and changing the values there as appropriate. Then, create the initial
database schema with ``python manage.py migrate``.

EditGroups has three components: the web server, the edit listener and the Celery tasks backend.

For the web server, just use ``python manage.py runserver`` and this will
start a local web server, you can then access your EditGroups instance at ``http://localhost:8000/``.

By default, there will not be much to see as the database will be empty. To get some data in, you need
to run the listener script, which reads the Wikidata event stream and populates the database::

    python listener.py

You will also need to run Celery, which will periodically annotate edits which need inspection,
as well as providing the undo functionality (if you have set up OAuth, see below)::

    ./celery.sh

With these three components running in parallel you should have a working version of EditGroups to
work on.

Configuring the supported tools
-------------------------------

EditGroups works by matching regular expressions on edit summaries to detect the tools responsible
for them and the unique id of the batch they belong to. As the set of tools running on a given
wiki will generally vary (as well as the format of the edit summaries they use), these regular
expressions are treated as user data in EditGroups: they are stored in the database and are configured
from Django's admin interface, which can befound at `http://localhost:8000/admin/` if the
instance is running locally. To access this interface, you will need to have a super-user account,
which can be created with the ``./manage.py createsuperuser`` command.

To add a tool, go to ``http://localhost:8000/admin/store/tool/`` and click **Add tool**. You will need
to fill in the following fields:

- **Name**: the name of the tool, displayed in the interface
- **Shortid**: a short identifier for the tool, used in the URLs for its batches. For instance, ``OR`` is the short id for OpenRefine in the Wikidata instance, which can be seen in URLs such as ``https://tools.wmflabs.org/editgroups/b/OR/28d99182/``;
- **Idregex**: a Python regular expression which captures the batch identifier in the edit summary. The batch identifier must be captured by a group. For instance you could use ``.*editgroups/b/OR/([a-f0-9]{4,32})\|details\]\]\).*`` for OpenRefine.
- **Idgroupid**: the numerical identifier of the group to extract from the regex above to obtain the batch identifier (1 in the example above)
- **Summaryregex**: a Python regular expression which captures the batch summary from the edit summary. Again a group must capture the relevant part to extract.
- **Summarygroupid**: the numerical identifier of the group to extract to obtain the batch summary.
- **Userregex** and **Usergroupid** can be used in a similar way to extract the username on behalf of which the edit group is made (if any). This is optional.
- **URL**: a web address where a description of the tool can be found.

Once you validate this form, the edits listener will pick up the new tool (after a few minutes) and start ingesting its edits. If you 
need to ingest past edits again, you can use the listener script with a date in the past to retrieve the previous edits.

Deploying on WMF Toollabs
-------------------------

In what follows we assume that the tool is deployed as the ``editgroups`` project.

-  ``become editgroups``
-  ``mkdir -p www/python/src``

Install the dependencies in the virtualenv::

  cd www/python
  virtualenv venv --python /usr/bin/python3
  source venv/bin/activate
  git clone https://github.com/Wikidata/editgroups.git src
  pip install -r src/requirements.txt

Configure static files::

  mkdir -p src/static
  ln -s src/static

Put the following content in ``~/www/uwsgi.ini``::

  [uwsgi]
  check-static = /data/project/editgroups/www/python

and run ``./manage.py collectstatic``.

Create the SQL database:

- ``sql tools`` 
- ``CREATE DATABASE s1234__editgroups;`` where ``s1234`` is the SQL username of the tool
- ``\q``

Configure database access and other settings::

  cd ~/www/python/src/editgroups/settings/
  echo "from .prod import *" > __init__.py
  cp secret_wmflabs.py secret.py

Edit ``secret.py`` with the user
and password of the table (they can be found in ``~/replica.my.cnf``).
The name of the table is the one you used at creation above
(``s1234__editgroups`` where ``s1234`` is replaced by the username of
the tool).

Configure OAuth login:

- Request an OAuth client id at https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose. Beyond the normal editing scopes, you will also need to perform administrative actions (delete, restore) on behalf of users, so make sure you request these scopes too.
- Put the tokens in ``~/www/python/src/editgroups/settings/secret.py``

Migrate the database:

- ``./manage.py migrate``

Run the webserver:

- ``webservice --backend kubernetes python start``

Launch the listener and Celery in Kubernetes:

- ``kubectl create -f deployment/listener.yaml``
- ``kubectl create -f deployment/celery.yaml``

Backup the database regularly with:

- ``mysqldump -C s1234__editgroups | gzip > database_dump.gz``

