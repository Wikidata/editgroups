#!/bin/bash
kubectl delete deployment editgroups.listener.sh && kubectl create -f /data/project/editgroups/www/python/src/deployment.yaml && kubectl get pods
