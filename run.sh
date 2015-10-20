#!/bin/bash

set -ex

docker build --tag=d https://raw.githubusercontent.com/TomasTomecek/fedora-portal-content-verifier/master/Dockerfile

for module in $(find . -maxdepth 1 -type d -not -path "." -not -path "./.git") ; do
  docker run \
    --privileged \
    -e DOCKER_DAEMON_ARGS="-D -l debug" \  # -s <graph_backend>
    --rm \
    -it \
    d $module
done
