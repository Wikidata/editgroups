#!/bin/bash
export GOMAXPROCS=1
TOOLNAME=$(whoami | cut -d "." -f 2)
echo "Running as ${TOOLNAME}"

if [[ "$TOOLNAME" == "editgroups" ]]; then
  CELERY_FN=celery
else
  CELERY_FN="celery-${TOOLNAME}"
fi

kubectl delete deployment "${TOOLNAME}.celery.sh";
echo "Waiting for Celery to stop";
sleep 45;
kubectl create -f "/data/project/${TOOLNAME}/www/python/src/deployment/${CELERY_FN}.yaml"
