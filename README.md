# waisn-tech-tools

Tech tools for the WAISN.

# Setting up Environment

[Anaconda][] is used to manage the python environment that the project runs in. After installing, you can set up the
anaconda environment:

```
# create the conda env
conda env create -f ./environment.yml
# 'waisn-tech-tools' conda env should be listed
conda env list
# activate the environment
source activate waisn-tech-tools
# do a bunch of work
# ...
# ...
# deactivate the env
source deactivate
```

The integration tests use Selenium with the Firefox browser running in headless mode. You will need to install
**geckodriver** to run these tests.

[Anaconda]: https://www.anaconda.com/

# Updating the Environment

If you are installing new packages, you will want to update the environment file as well.

```
# install new package
conda install new-package-name
# update environment file for mac environment
conda env export > ./environment-mac.yml
# please remove the "prefix" key from the file
```

There is a separate environment file for the Docker image. This is because the library versions are different for the
different OS's. The Docker image is built on top of the Ubuntu base image and hence the library versions in the file
refer to Linux versions. Updating this file requires a few more steps compared to updaing the environment for local
development:

```
# run the Docker image but using a shell as the entry point
docker run -ti --entrypoint /bin/bash ${IMAGE_ID}
# you should be in a shell in the Docker container at this point
# activate the Conda env
conda activate waisn-tech-tools
conda install ${NEW_PKG}
# update the environment file
cd /opt/waisn-tech-tools/
conda env export > environment-docker.yml
exit
# you should now be in the local host's shell
docker cp ${CONTAINER_ID}:/opt/waisn-tech-tools/environment-docker.yml .
# edit file to remove **prefix** section
```

# Project Commands

To see commands specific to the project, e.g. seeding, run:

```
python manage.py
```

# Running the Server Locally

There are a few environment settings that need to be enabled to run the server. The reason for this is because the
website is protected using Auth0. Hence the following environment variables need to be declared. Note that the Auth0
application should be configured to be a **Regular Web Application**.

* `AUTH0_DOMAIN`: The Auth0 application's domain
* `AUTH0_KEY`: The Auth0 application's client id
* `AUTH0_SECRET`: The Auth0 application's client secret.
* `TWILIO_ACCOUNT_SID`: Twilio Account SID for client
* `TWILIO_AUTH_TOKEN`: Twilio Auth Token for client
* `TWILIO_SMS_NUMBER`: Phone number bought through Twilio for client

## Disabling Auth0

Runnning the service locally without access to the internet requires authentication to be disabled. This can be done by
setting the environment variable:

```
# disable Auth0 login requirement
export WAISN_AUTH_ENABLED='FALSE'
```

## Setting up Twilio

You can set up a free Twilio account and then get a trial number, which is also free. You will then use the account
credentials (the account SID & auth token) and the SMS number as environment variables.

If you are running this locally, then you will need to create a tunnel from a public end-point to the local service. We
recommend using [ngrok][] to do so, which is free. Start ngrok after spinning up the service:

```
# start the service
python manage.py runserver
# create a tunnel to the port that Django starts on
ngrok http 8000
```

A dashboard will start in the terminal providing the forwarding DNS e.g. **http://6c465057.ngrok.io**. Using this DNS,
go to the Twilio console:

1. Go to **Phone Numbers**
1. Click the number that you are using for Twilio
1. Go to the **Messaging** section
1. Change the value of the webhook for **A MESSAGE COMES IN** to **${NGROK_DNS}/alerts/subscribe**

You can now send messages to that phone number and interact with the Django Service.

[ngrok]: https://ngrok.com/

# Running the Server in Production

There are two settings configurations:
* **Development**: `waisntechtools/waisntechtools/settings/development.py`
* **Production**: `waisntechtools/waisntechtools/settings/production.py`

The production settings file should be used, naturally, in production. Settings files can be specified via the Django
`runserver` command i.e.:

```
python ./manage.py runserver --settings waisntechtools.settings.production
```

There are additional environment settings that need to be set:

* `DJANGO_SECRET_KEY`: See [Django SECRET_KEY Docs][]
* `RDS_HOSTNAME`: database hostname
* `RDS_PORT`: port the database server is listening on
* `RDS_DB_NAME`: name of database to use
* `RDS_USERNAME`: username used to access the database
* `RDS_PASSWORD`: password used to access the database

[Django SECRET_KEY Docs]: https://docs.djangoproject.com/en/2.2/ref/settings/#std:setting-SECRET_KEY

# Docker

## Development Image

You can build the web application using the provided Docker file. This **Dockerfile** uses a
[Docker Multi-Stage Build][] to build both the development and production Docker images. This is done because in allows
inheriting the common Dockerfile segments.

```
# build the development Docker image: must be in the same directory as the Dockerfile file
docker build . --target waisntechtools-dev
# run the docker file
docker run -p 8000:8000 --rm [environment variables] ${IMAGE_ID}
```

[Docker Multi-Stage Build]: https://docs.docker.com/develop/develop-images/multistage-build/

## Production Image

Build the production image using a similar command for the development, but changing the target:

```
# build the prod Docker image
docker build . --target waisntechtools-prod
```

If you want to test the production docker image, you will need to have a MySQL server running. One possible approach is
you can spin up a [MariaDB Docker container][].

```
# spin up the MariaDB container port forwarding 5000 on the local host to 3306 in the Docker container
docker run -p 5000:3306 --rm --name waisn-mariadb -e MYSQL_ROOT_PASSWORD=pw -d mariadb:latest
# verify that we can connect to it using the MySQL client (you will be prompted to put in the password)
mysql -h 127.0.0.1 -P 5000 -u root -p
# create the database used by the service
MariaDB [(none)]> create database waisntechtools;
```

Before using the production image, let's first try to get the service running locally and using the MariaDB container
as the DB:

```
# run the needed migrations
export DJANGO_SECRET_KEY=KEY; \
  export RDS_HOSTNAME=127.0.0.1; \
  export RDS_PORT=5000; \
  export RDS_DB_NAME=waisntechtools; \
  export RDS_USERNAME=root; \
  export RDS_PASSWORD=pw; \
  python manage.py migrate --settings waisntechtools.settings.production
# run the server
export DJANGO_SECRET_KEY=KEY; \
  export RDS_HOSTNAME=127.0.0.1; \
  export RDS_PORT=5000; \
  export RDS_DB_NAME=waisntechtools; \
  export RDS_USERNAME=root; \
  export RDS_PASSWORD=pw; \
  python manage.py runserver --settings waisntechtools.settings.production
```

Sweetness. Let's now run the server in a Docker container. Because this will run the server in the default Docker
bridge, [we cannot use DNS resolution][] using the Docker container name. Hence, we'll need to figure out the IP address
of the container in the default network:

```
docker inspect -f '{{.NetworkSettings.Networks.bridge.IPAddress}}' waisn-mariadb
```

We can then use this IP address to connect the WAISN Docker container to the MariaDB:

```
# while we've already run migrations, if you have authentication enabled, you'll need to run it again because with
# authentication, the Auth0 tables need to be created.
# Notice that we use the port in the Docker network instead of the one exposed on the host.
docker run -p 8000:8000 --rm -d \
    -e AUTH0_DOMAIN=VALUE \
    -e AUTH0_KEY=VALUE \
    -e AUTH0_SECRET=VALUE \
    -e DJANGO_SECRET_KEY=VALUE \
    -e RDS_HOSTNAME=${DB_CONTAINER_IP_ADDR} \
    -e RDS_PORT=3306 \
    -e RDS_DB_NAME=waisntechtools \
    -e RDS_USERNAME=root \
    -e RDS_PASSWORD=pw \
    ${IMAGE_ID}
```

[MariaDB Docker container]: https://hub.docker.com/_/mariadb
[we cannot use DNS resolution]: https://docs.docker.com/v17.09/engine/userguide/networking/#the-default-bridge-network
