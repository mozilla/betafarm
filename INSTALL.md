From an email from paul osman:



Here are the steps I take to get it up and running on OS X.

Note: I use virtualenvwrapper to manage virtualenvs, but you can also use vanilla virtualenv. Just replace 'mkvirtualenv betafarm' below with 'pip install virtualenv; virtualenv /path/to/a/virtualenv; source /path/to/a/virtualenv/bin/activate;'.

1) Install MySQL. There are a variety of ways to do this on OS X, I prefer homebrew but YMMV.

2) Check out betafarm. Make sure to use --recursive so you get all of the git submodules under vendor/

$ git clone --recursive git@github.com:mozilla/betafarm.git
…

3) Create virtualenv and install dependencies:

$ cd betafarm
$ mkvirtualenv betafarm
$ pip install -r requirements/dev.txt
$ pip install -r requirements/compiled.txt

4) create local settings file. Edit the file and set at a minimum a database name, user, etc. I just use 'root' on local dev machines.
$ cp settings_local.py-dist settings_local.py
$ emacs settings_local.py
…
(be sure to specify the database name ('betafarm' is used below) and the username (root is used below).

Also add HMAC_KEYS as indicated in the docs for django-sha2 docs.

5) Create the database
$ echo "create database betafarm" | mysql -uroot

6) Optional - run tests
$ python manage.py test

7) Create tables and run db migrations.
$ python manage.py syncdb
$ python manage.py migrate

8) Try it out.
$ python manage.py runserver

If everything worked, you should have a web server running on port 8000. 


