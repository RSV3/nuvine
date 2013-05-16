#!/bin/sh

if [ $# == 1 ]
then
  heroku pgbackups:restore DATABASE `heroku pgbackups:url $1 --app winedora` --app winedora-alpha
else
  heroku pgbackups:restore DATABASE `heroku pgbackups:url --app winedora` --app winedora-alpha
fi
