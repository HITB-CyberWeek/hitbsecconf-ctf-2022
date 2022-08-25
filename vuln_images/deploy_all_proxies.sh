#!/bin/bash

set -e

prepared=0
for deploy_yaml in ../services/*/deploy.yaml
do
  # We need to run preparation steps only once
  if [[ $prepared == 0 && $1 != "--skip-preparation" ]]
  then
    ./deploy_proxies.py --prepare-only "$deploy_yaml"
    prepared=1
  fi

  # Skip preparation (because it's done already) and deploy proxies!
  ./deploy_proxies.py --skip-preparation --skip-dns "$deploy_yaml"
done
