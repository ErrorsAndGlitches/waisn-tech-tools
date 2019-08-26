#!/usr/bin/env bash
#
# This should only be run on one of the hosts in the web service fleet!

set -ex

MIGRATE_CMD=$(cat <<-END
. /opt/conda/etc/profile.d/conda.sh &&
 conda activate waisn-tech-tools &&
 cd /opt/waisn-tech-tools/waisntechtools &&
 python ./manage.py migrate --no-input --settings waisntechtools.settings.production
END
)
MIGRATE_CMD_NO_NEW_LINE=$(echo "$MIGRATE_CMD" | tr -d "\n")

docker run \
  -e RDS_HOSTNAME -e RDS_PORT -e RDS_USERNAME -e RDS_PASSWORD -e RDS_DB_NAME \
  --entrypoint /bin/bash errorsandglitches/waisn-tech-tools-prod \
  -c "$MIGRATE_CMD_NO_NEW_LINE"
