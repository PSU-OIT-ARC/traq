#!/bin/bash
mysql_user="${1:-${USER}_a}"
local_db_name="traq"
dump_file="traq.prod.dump"

echo "This script will load production Traq data into your local '${local_db_name}' database."
echo "It will DROP the local '${local_db_name}' database if it exists."
echo

echo "It's going to connect to the production database as '${mysql_user}'."
echo "If that's incorrect, abort and pass the correct user name on the command line."
echo

if [ -e "${dump_file}" ]; then
    echo "Removing dump file: ${dump_file}"
    rm -f $dump_file
fi

echo "Dumping production Traq data into '${dump_file}..."
mysqldump --user ${USER}_a --host mysql.rc.pdx.edu --databases traq --password > "${dump_file}"
echo "Dropping local '${local_db_name}' database..."
mysql -u root -e "drop database ${local_db_name}"
echo "Creating local '${local_db_name}' database..."
mysql -u root -e "create database ${local_db_name}"
echo "Loading prod data into local '${local_db_name}' database..."
mysql -u root < "${dump_file}"
echo "Done."
