#!/bin/bash

set -ex

dnf install -y docker git

cd /

git clone https://github.com/TomasTomecek/fedora-portal-content-verifier repo
cd repo

./wrapdocker

# docker is now running, let's test

./docker-compose/verify.sh
