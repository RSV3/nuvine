#!/bin/sh

heroku pgbackups:restore DATABASE `heroku pgbackups:url --app winedora` --app winedora-staging
