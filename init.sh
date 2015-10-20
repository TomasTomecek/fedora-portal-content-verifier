#!/bin/bash

set -ex

echo "Running init.sh with args ${@}"

cd /

git clone https://github.com/TomasTomecek/fedora-portal-content-verifier repo
cd repo

./wrapdocker

# docker is now running, let's test

./${1}/verify.sh
