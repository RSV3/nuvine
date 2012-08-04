# Setup Git

* Get SSH key setup with github
  * https://help.github.com/articles/generating-ssh-keys

* Install git with MacPorts
  
  $ sudo port install git-core

* Clone repository

  $ git clone git@github.com:RSV3/nuvine.git

# Setup Heroku

* Create a Heroku account at http://www.heroku.com
  * If you want to also deploy and test

* Install Heroku command line tools (Heroku toolbelt)
  * Download from https://toolbelt.herokuapp.com/
  * https://devcenter.heroku.com/articles/heroku-command

# Install virtualenv

  $ cd nuvine
  $ virtualenv-2.7 nuvine-env --distribute
  $ source nuvine-env/bin/activate
  $ pip install -r requirements.txt

  * You might have to install some dependencies

# Rename settings files for local development

  $ cd winedora
  $ mv settings_debug.py.rename settings_debug.py
  $ mv settings_local.py.rename settings_local.py

# Edit settings_local.py to specify absolute path of sqlite db directory 

  * defaults to: DATABASES = {'default': dj_database_url.config(default='sqlite:////Users/kwan/workspace/nuvine/winedora.test.db')}

# Run server in the nuvine directory (assuming you are in winedora directory)

  $ cd ..
  $ python manage.py syncdb
  $ python manage.py migrate
  $ python manage.py runserver
  


  
