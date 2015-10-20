#!/bin/bash

set -ex

docker build --tag=d git://github.com/TomasTomecek/fedora-portal-content-verifier

for module in $(find . -maxdepth 1 -type d -not -path "." -not -path "./.git") ; do
  echo "-- Testing \"${module}\" --"
  # -s <graph_backend>
  docker run \
    --privileged \
    -e DOCKER_DAEMON_ARGS="-D -l debug" \
    --rm \
    -it \
    d $module
done
