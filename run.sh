#!/bin/bash

set -ex

docker run \
  --privileged \
  -e DOCKER_DAEMON_ARGS="-s devicemapper -D -l debug" \
  --rm \
  -it \
  fedora:22 \
  bash -c "curl -o /init.sh https://raw.githubusercontent.com/TomasTomecek/fedora-portal-content-verifier/master/init.sh ; chmod +x /init.sh ; /init.sh"
