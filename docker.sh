#!/bin/bash


TAGGED_NAME="psuarc/traq"
EXPORT_PATH=`pwd`/..

CONFIG_PATH="docker/${1:-debian}"
MODE=${2:-client}
VERSION=${3:-master}

spawn()
{
  cd ${CONFIG_PATH}
  echo "Creating docker image '${TAGGED_NAME}'"
  sudo docker build \
      -t ${TAGGED_NAME} .

  echo "Spawning docker container with image traq@${VERSION}"
  echo "Mapping docker volume /opt/host=${EXPORT_PATH}"
  sudo docker run \
      -p 127.0.0.1:8000:80 \
      -v ${EXPORT_PATH}:/opt/host \
      -e VERSION=${VERSION} \
      -e BUILD_MODE=${MODE} \
      -i -t ${TAGGED_NAME} \
      /bin/bash
}


if [[ $# -gt 2 ]]; then
  echo "Usage: ./docker.sh [config] [[client] | clone] [version]"
  exit
else
  spawn
fi
