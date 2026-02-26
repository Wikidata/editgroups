FROM docker-registry.tools.wmflabs.org/toolforge-python311-sssd-web:latest

WORKDIR /root/www/python/

RUN apt-get update && apt-get install -y \
    gcc \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    git \
    netcat-openbsd \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Necessary flags for mysqlclient driver
ENV MYSQLCLIENT_CFLAGS="-I/usr/include/mariadb/"
ENV MYSQLCLIENT_LDFLAGS="-L/usr/lib/x86_64-linux-gnu/ -lmariadb"
ENV VIRTUAL_ENV /root/www/python/venv
ENV PATH="/root/www/python/venv/bin:${PATH}"
ENV DJANGO_SETTINGS_MODULE=editgroups.settings
ENV PYTHONPATH="/root/www/python/src:${PYTHONPATH}"
COPY requirements.txt ./src/requirements.txt
RUN echo "mysqlclient==2.2.7" >> /root/www/python/src/requirements.txt
RUN webservice-python-bootstrap

COPY . ./src
WORKDIR /root/www/python/src/

RUN echo "from .dev import *" > /root/www/python/src/editgroups/settings/__init__.py
COPY editgroups/settings/docker.py /root/www/python/src/editgroups/settings/secret.py
RUN echo "source /root/www/python/venv/bin/activate" >> /root/.bashrc # useful when entering the shell

# Just to make sure virtual environment is working properly
RUN ["/bin/bash", "-c", "source ../venv/bin/activate && python3 manage.py collectstatic --no-input"]

EXPOSE 8000
