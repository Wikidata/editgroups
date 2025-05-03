#!/bin/bash
celery --app=editgroups.celery:app worker --concurrency=1 --max-memory-per-child=50000 -B -l INFO

