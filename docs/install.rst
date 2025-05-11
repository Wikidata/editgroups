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
- **Shortid**: a short identifier for the tool, used in the URLs for its batches. For instance, ``OR`` is the short id for OpenRefine in the Wikidata instance, which can be seen in URLs such as ``https://editgroups.toolforge.org/b/OR/28d99182/``;
- **Idregex**: a Python regular expression which captures the batch identifier in the edit summary. The batch identifier must be captured by a group. For instance you could use ``.*editgroups/b/OR/([a-f0-9]{4,32})\|details\]\]\).*`` for OpenRefine.
- **Idgroupid**: the numerical identifier of the group to extract from the regex above to obtain the batch identifier (1 in the example above)
- **Summaryregex**: a Python regular expression which captures the batch summary from the edit summary. Again a group must capture the relevant part to extract.
- **Summarygroupid**: the numerical identifier of the group to extract to obtain the batch summary.
- **Userregex** and **Usergroupid** can be used in a similar way to extract the username on behalf of which the edit group is made (if any). This is optional.
- **URL**: a web address where a description of the tool can be found.

Once you validate this form, the edits listener will pick up the new tool (after a few minutes) and start ingesting its edits. If you 
need to ingest past edits again, you can use the listener script with a date in the past to retrieve the previous edits.

Deploying on WMF Toolforge
--------------------------

In what follows we assume that the tool is deployed as the ``editgroups`` project.

-  ``become editgroups``
-  ``mkdir -p www/python/src``

Put the following contents in ``service.template`` in the home directory of the tool::

  backend: kubernetes
  type: python3.11

Install the dependencies in the virtualenv::

  webservice shell
  cd www/python
  python3 -m venv venv
  source venv/bin/activate
  pip install --upgrade pip
  git clone https://github.com/Wikidata/editgroups.git src
  pip install -r src/requirements.txt

Configure static files::

  mkdir -p src/static
  ln -s src/static .

Create the SQL database (outside of the ``webservice shell``):

- ``sql tools`` 
- ``CREATE DATABASE s1234__editgroups;`` where ``s1234`` is the SQL username of the tool (can be found in ``~/replica.my.cnf``)
- ``\q``

Configure database access and other settings::

  cd ~/www/python/src/editgroups/settings/
  echo "from .prod import *" > __init__.py
  cp secret_toolforge.py secret.py

Edit ``secret.py`` with the user
and password of the table (they can be found in ``~/replica.my.cnf``).
The name of the table is the one you used at creation above
(``s1234__editgroups`` where ``s1234`` is replaced by the username of
the tool). Also, pick a secret key to store in ``SECRET_KEY``.

In the ``editgroups/settings/__init__.py`` you can also copy over
settings line from ``editgroups/settings/common.py`` and adapt them to
the wiki that you are running EditGroups for (for instance ``MEDIAWIKI_API_ENDPOINT`` and the following lines).
You should also adapt the allowed hostname (taken from ``editgroups/settings/prod.py``). It's easier
to add those to the ``__init__.py`` file to avoid editing files tracked by Git.

Set up a redis container for the service, following instructions at https://wikitech.wikimedia.org/wiki/Tool:Containers#Redis_container.
The password and host name of the redis container need to be inserted in `editgroups/settings/secret.py` as `REDIS_PASSWORD` and `REDIS_HOST` respectively.

Put the following content in ``~/www/python/uwsgi.ini``::

  [uwsgi]
  static-map = /static=/data/project/editgroups/www/python/src/static

  master = true
  attach-daemon = /data/project/editgroups/www/python/venv/bin/python3 /data/project/editgroups/www/python/src/listener.py

and run ``./manage.py collectstatic`` in the ``~/www/python/src`` directory. The listener will be an attached dameon, restarting with webservice restart.


Configure OAuth login:

- Request an OAuth client id at https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose. As OAuth protocol version, use "OAuth 1.0a". As callback URL, use the domain of the tool and tick the box to treat it as a prefix. Beyond the normal editing scopes, you will also need to perform administrative actions (delete, restore) on behalf of users, so make sure you request these scopes too.
- Put the tokens in ``~/www/python/src/editgroups/settings/secret.py``

Migrate the database:

- ``./manage.py migrate``

Run the webserver:

- ``webservice start``

Go to the webservice, login with OAuth to the application. This will create a ``User`` object that you can then mark as staff in the Django shell, as follows::

   $ webservice shell
   source ~/www/python/venv/bin/activate
   cd www/python/src
   ./manage.py shell
   from django.contrib.auth.models import User
   user = User.objects.get()
   user.is_staff = True
   user.save()

Launch Celery in Kubernetes. These deployment files may need to be adapted if you are not deploying the tool as the ``editgroups`` toolforge tool but another tool id:

- ``kubectl create -f deployment/celery.yaml``

Backup the database regularly with:

- ``mysqldump -C s1234__editgroups | gzip > database_dump.gz``

