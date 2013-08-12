nuvine
======

Fresh start for Vinely site

Release Notes
======


Install
======

- To initialize completely new system
	- python manage.py syncdb (do not create admin account)
	- python manage.py accounts/fixtures/groups.yaml
	- python manage.py migrate 


Development Setup
=================

- On Dev
  - python manage.py calculate_weekly_sales  (4 am, once daily)
  - python manage.py traverse_pro_tree -l -b (4 am, once daily)

- On Staging
  - python manage.py update_orders
  - python manage.py set_mentor_to_current_pro