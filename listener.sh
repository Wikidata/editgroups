#!/usr/bin/env bash

set -e

VENV_DIR=/data/project/editgroups/www/python/venv

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
echo "Launching listener"
python3 listener.py
echo "Listener terminated"
