#!/bin/sh

java -jar schemaSpy_5.0.0.jar -t pgsql -dp /opt/local/share/java/postgresql.jar -host localhost:5432 -db winedora -s public -u vinely -p winedora -o schemahtml
