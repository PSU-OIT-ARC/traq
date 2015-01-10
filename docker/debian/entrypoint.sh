#!/bin/bash


# Unpack Traq codebase and bootstrap application
BASE_PATH="/webapps"
PROJECT_NAME='traq'

echo "Starting services..."
service apache2 start
service mysql start
service supervisor start

if [[ ! -d "${BASE_PATH}" ]]; then
  mkdir ${BASE_PATH}
  cd ${BASE_PATH}
fi

echo "Checking out version $1..."
git clone file:///opt/host/${PROJECT_NAME} ${PROJECT_NAME}
cd ${PROJECT_NAME}
git remote set-url origin https://github.com/PSU-OIT-ARC/traq.git
git checkout "$1"

echo "Cloning configuration..."
cp /opt/host/${PROJECT_NAME}/traq/local_settings.docker.py traq/local_settings.py

echo "Bootstrapping..."
virtualenv --no-site-packages --python=python3 .env
source .env/bin/activate
make install

echo "Configuring file system..."
if [[ ! -d "media" ]]; then
  ln -sv /opt/host/${PROJECT_NAME}/media .
fi

exec /bin/bash
