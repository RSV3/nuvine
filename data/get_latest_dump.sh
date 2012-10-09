#!/bin/sh

# usage: ./get_latest_dump.sh winedora
# usage: ./get_latest_dump.sh winedora-staging

curl -o latest.dump `heroku pgbackups:url -a $1`
pg_restore --verbose --clean --no-acl --no-owner -h localhost -U vinely -d winedora latest.dump
