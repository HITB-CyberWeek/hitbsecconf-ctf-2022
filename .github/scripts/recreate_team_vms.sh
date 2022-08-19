#!/bin/bash

set -ex

SERVICE_NAME="$1"

cd /cloud/backend
service_id=$(grep -E ^$SERVICE_NAME\\s db/services.txt | awk '{print $2}')

for team in `seq 1 2`
do
   ./restore_vm_from_snapshot.py $team $service_id init
done
