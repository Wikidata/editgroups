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

When working on EditGroups, you can run it locally. Just use ``python manage.py runserver`` and this will
start a local web server, you can then access your EditGroups instance at ``http://localhost:8000/``.

By default, there will not be much to see as the database will be empty.

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

put the following content in ``~/www/uwsgi.ini``::

  [uwsgi]
  check-static = /data/project/editgroups/www/python

-  run ``./manage.py collectstatic``

Create the SQL database:
- ``sql tools`` 
- ``CREATE DATABASE s1234__editgroups;`` where ``s1234`` is the SQL
username of the tool
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
- Request an OAuth client id at
https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose. Beyond the normal editing scopes, you will also need to perform administrative actions (delete, restore) on behalf of users, so make sure you request these scopes too.
- Put the tokens in
``~/www/python/src/editgroups/settings/secret.py``

Migrate the database:
- ``./manage.py migrate``

Run the webserver:
- ``webservice --backend kubernetes python start``

Backup the database regularly with:
- ``mysqldump -C s1234__editgroups | gzip > database_dump.gz``

