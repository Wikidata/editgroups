#!/bin/bash
kubectl delete deployment editgroups.listener.sh && kubectl create -f /data/project/editgroups/www/python/src/deployment/listener.yaml && kubectl get pods
