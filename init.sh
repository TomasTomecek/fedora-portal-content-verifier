#!/bin/bash

set -ex

cd /

git clone https://github.com/TomasTomecek/fedora-portal-content-verifier repo
cd repo

./wrapdocker

# docker is now running, let's test

./${1}/verify.sh
