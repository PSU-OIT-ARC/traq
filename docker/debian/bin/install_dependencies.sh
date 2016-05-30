#!/bin/bash

LOCAL_PATH=/usr/local/docker
export DEBIAN_FRONTEND=noninteractive

# Refresh local APT cache
apt-get update && \
    apt-get -y upgrade

# Install project build dependencies
apt-get install -y \
    make \
    libfreetype6-dev libjpeg-dev libpng-dev \
    python3-dev \
    mysql-server mysql-client \
    supervisor

cp ${LOCAL_PATH}/conf/supervisor/celery.conf /etc/supervisor/conf.d/
a2enmod expires
a2enmod xsendfile
echo "Installing Traq VHOST..."
cp ${LOCAL_PATH}/conf/apache/sites/traq.research.pdx.edu.conf /etc/apache2/sites-available
a2ensite traq.research.pdx.edu.conf
