#!/bin/bash

set -ex

# prereq #1 -- docker-compose package

dnf install -y docker-compose git elinks docker


# prereq #2 -- images used in the guide

cd /
git clone https://github.com/fedora-cloud/Fedora-Dockerfiles
docker build --tag=fedora-django Fedora-Dockerfiles/Django
docker build --tag=fedora-postgresql Fedora-Dockerfiles/postgresql

# guide testing

cd /
mkdir awesome_web
cd awesome_web
mkdir db
chown 26:26 db
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

cat >>awesome_web/awesome_web/settings.py <<EOF
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'awesome_web',
        'USER': 'awesome_web_user',
        'PASSWORD': 'secret_password',
        'HOST': 'db',
        'PORT': 5432,
    }
}
EOF

docker-compose up -d db
docker-compose run web python manage.py migrate
docker-compose up -d
elinks -dump http://$(docker inspect -f '{{ .NetworkSettings.IPAddress }}' awesomeweb_web_1):8000
