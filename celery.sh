#!/bin/bash
celery --app=editgroups.celery:app worker -B -l INFO

