#!/bin/bash

# usage: ./get_latest_dump.sh winedora
# usage: ./get_latest_dump.sh winedora-staging
# usage: ./get_latest_dump.sh winedora b090

if [ $# == 2 ]
then
  curl -o latest.dump `heroku pgbackups:url $2 -a $1`
  pg_restore --verbose --clean --no-acl --no-owner -h localhost -U vinely -d winedora latest.dump
  echo "Restored db $2 from $1"
else
  curl -o latest.dump `heroku pgbackups:url -a $1`
  pg_restore --verbose --clean --no-acl --no-owner -h localhost -U vinely -d winedora latest.dump
  echo "Restored latest backup db from $1"
fi
