Wikidata edit groups
====================

[![Build Status](https://travis-ci.org/wetneb/editgroups.svg?branch=master)](https://travis-ci.org/wetneb/editgroups) [![Coverage Status](https://coveralls.io/repos/github/wetneb/editgroups/badge.svg?branch=master)](https://coveralls.io/github/wetneb/editgroups?branch=master)

Simple tool to track edit groups on Wikidata and revert them.


Steps to deploy this on WMF Toolslab:

* `become editgroups`
* `mkdir -p www/python/src`

Install the dependencies in the virtualenv:
* `cd www/python`
* `virtualenv venv --python /usr/bin/python3`
* `source venv/bin/activate`
* `git clone https://github.com/wetneb/editgroups.git src`
* `pip install -r src/requirements.txt`

Configure static files
* `mkdir -p src/static`
* `ln -s src/static .`
* put the following content in `~/www/uwsgi.ini`:

    [uwsgi]
    check-static = /data/project/editgroups/www/python

* run `./manage.py collectstatic`


Create database:
* `sql tools`
* `CREATE DATABASE s1234__editgroups;` where `s1234` is the SQL username of the tool
* `\q`

Configure database access and other settings
* `cd ~/www/python/src/editgroups/settings/`
* `echo "from .prod import *" > __init__.py`
* `cp secret_wmflabs.py secret.py`
* edit `secret.py` with the user and password of the table (they can be found in `~/replica.my.cnf`). The name of the table is the one you used at creation above (`s1234__editgroups` where `s1234` is replaced by the username of the tool).

Configure OAuth login
* Request an OAuth client id at https://meta.wikimedia.org/wiki/Special:OAuthConsumerRegistration/propose
* Put the tokens in `~/www/python/src/editgroups/settings/secret.py`

Migrate the database
* `./manage.py migrate`

Run the webserver
* `webservice --backend kubernetes python start`

