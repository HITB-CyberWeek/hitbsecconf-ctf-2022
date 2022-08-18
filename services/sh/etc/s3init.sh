#!/bin/sh -x

sleep 3

mc alias set s3 http://s3:9000 ${MINIO_ROOT_USER} ${MINIO_ROOT_PASSWORD}

mc admin policy add s3 readappend /opt/policy.json
mc admin user add s3 ${MINIO_SH_USER} ${MINIO_SH_PASSWORD}
mc admin policy set s3 readappend user=${MINIO_SH_USER}
