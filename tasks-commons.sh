#!/usr/bin/env bash


VENV_DIR=/data/project/editgroups-commons/www/python/venv

if [[ -f ${VENV_DIR}/bin/activate ]]; then
      source ${VENV_DIR}/bin/activate
else
      echo "Creating virtualenv"
      rm -rf ${VENV_DIR}
      pyvenv ${VENV_DIR}
      source ${VENV_DIR}/bin/activate
      echo "Installing requirements"
      pip install -r requirements.txt
fi;
echo "Starting celery"
export C_FORCE_ROOT=True
/data/project/editgroups-commons/www/python/venv/bin/python3 /data/project/editgroups-commons/www/python/venv/bin/celery --app=editgroups-commons.celery:app worker -l INFO -B  --concurrency=3 --max-memory-per-child=50000
echo $?
echo "Celery done"

