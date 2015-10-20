#!/bin/bash

set -ex

dnf install -y docker-compose \
  git  # used during the guide

prepare_docker_images() {
  cd /
  git clone https://github.com/fedora-cloud/Fedora-Dockerfiles
  docker build --tag=fedora-django Fedora-Dockerfiles/Django
  docker build --tag=fedora-postgresql Fedora-Dockerfiles/postgresql
}

cd /
mkdir awesome_web
cd awesome_web
mkdir db
sudo chown 26:26 db
cat >docker-compose.yml <<EOF
web:
  image: fedora-django
  ports:
   - "8000:8000"
  volumes:
   - ./awesome_web:/code
  links:
   - db
db:
  image: fedora-postgresql
  volumes:
   - ./db:/var/lib/pgsql/data
  environment:
   - POSTGRESQL_DATABASE=awesome_web
   - POSTGRESQL_USER=awesome_web_user
   - POSTGRESQL_PASSWORD=secret_password
EOF
docker-compose run web django-admin startproject awesome_web .
chown -R $UID:$UID awesome_web

