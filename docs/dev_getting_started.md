# Templates
  * winedora/templates/winedora/base_html5.html is the top html template that is extended by all templates
  * main/templates/main/menu_base.html and main/templates/main/menu_base_flip.html are used for templates that require a menu on left or right

# Code update from github

    $ git pull origin
  
# Setup so that your staging branch tracks origin/staging (at github)

    $ git branch --set-upstream staging origin/staging

# For checking in code

    $ git status (to see which files have changed)
    $ git add <file names> [or] git add . (to add all files)
    $ git commit -m "any comment on your changes"
  
# To push commits to github

    $ git push origin staging

# To push commits to heroku-staging

    $ git push heroku-staging staging:master

# To pull updates

    $ git pull origin staging
