#!/bin/sh

#
# Sync mode: SENDER
#
echo ""
echo "\033[90m#############################################\033[m"
echo "\033[94m[INFO]\033[m Testing sync mode: SENDER"
docker-compose exec www2 python3 /var/www/html/sync.py -f /var/www/html/test/scenario/sender/sync-local-to-www1.json -m

# Expecting 3 results in the database
count=$(docker-compose exec db1 mysql -udb -pdb db -e 'SELECT COUNT(*) FROM person' | grep 3 | tr -d '[:space:]')
if [ $count == '|3|' ]; then
    echo "\033[92m[SUCCESS]\033[m Synchronisation succeeded"
    echo "\033[90m#############################################\033[m"
else
    echo "\033[91m[FAILURE]\033[m Synchronisation was not successful"
    echo "\033[90m#############################################\033[m"
    exit 1
fi
#
# Reset scenario
#
sh ../helper/cleanup.sh
