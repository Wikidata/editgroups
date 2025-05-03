#!/bin/bash
export GOMAXPROCS=1
kubectl delete deployment editgroups.celery.sh ;
echo "Waiting for Celery to stop";
sleep 45 ;
kubectl create -f /data/project/editgroups/www/python/src/deployment/celery.yaml && kubectl get pods
