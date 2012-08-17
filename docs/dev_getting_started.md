# Templates
  * winedora/templates/winedora/base_html5.html is the top html template that is extended by all templates
  * main/templates/main/menu_base.html and main/templates/main/menu_base_flip.html are used for templates that require a menu on left or right
  * main/templates/main contains most of the templates
  * accounts/templates/accounts/base_my_account.html also is the template that user account related templates inherit

# Code update from github

    $ git pull origin
  
# Setup so that your staging branch tracks origin/staging (at github)

    $ git branch --set-upstream staging origin/staging

# For checking in code

    $ git status (to see which files have changed)
    $ git add <file names> [or] git add . (to add all files) [or] git add -u (if you have deleted files also)
    $ git commit -m "any comment on your changes"
  
# To push commits to github

    $ git push origin staging

# To push commits to heroku-staging

    $ git push heroku-staging staging:master

# To pull latest updates

    $ git pull origin staging

# To runserver you need to be in the virtual environment and in the project root directory
  * The virtual environment is currently in nuvine-env inside the project directory
  * You should probably have an alias to activate the virtual environment, but if not

    $ source nuvine-env/bin/activate

  * run server which will be accessible from http://localhost:8000

    $ python manage.py runserver

# If you do not see any products in the Shop menu, run the following

    $ python manage.py refresh_products

# The following are series of commands that should be executed if you want to start with fresh db 

    $ git pull origin staging
    $ rm winedora.test.db
    $ python manage.py syncdb (make sure you say NO to admin user) 
    $ python manage.py refresh_products
