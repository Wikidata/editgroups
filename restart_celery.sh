#!/bin/bash
export GOMAXPROCS=1
kubectl delete deployment editgroups.celery.sh ; kubectl create -f /data/project/editgroups/www/python/src/deployment/celery.yaml && kubectl get pods
