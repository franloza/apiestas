.. image:: img/logo.png

|

.. image:: https://img.shields.io/github/license/Naereen/StrapDown.js.svg
   :target: https://github.com/franloza/apiestas/blob/master/LICENSE

Introduction
------------
Apiestas is a project composed of a backend powered by the awesome framework `FastAPI
<https://github.com/tiangolo/fastapi/>`_ and a crawler powered by `Scrapy
<https://github.com/scrapy/scrapy/>`_.

This project has followed code examples from *RealWorld apps*, specifically the following projects:

* `FastAPI RealWorld App <https://github.com/nsidnev/fastapi-realworld-example-app/>`_
* `FastAPI MongoDB RealWorld App <https://github.com/markqiu/fastapi-mongodb-realworld-example-app/>`_ (A fork of the previous)
* `Full Stack FastAPI PostgreSQL <https://github.com/tiangolo/full-stack-fastapi-postgresql/>`_


The crawler inserts and updates data from the MongoDB database by using the Apiestas REST API and the data is exposed through this API.
The REST API communicates with the database by using `Motor <https://github.com/mongodb/motor/>`_  - the async Python driver for MongoDB.
Finally, this application uses `Typer <https://github.com/tiangolo/typer/>`_ to create the Apiestas CLI, which is the main entrypoint of the application.

Quickstart
----------

First, set environment variables and create database. For example using ``docker``: ::

    export MONGO_DB=rwdb MONGO_PORT=5432 MONGO_USER=MONGO MONGO_PASSWORD=MONGO
    docker run --name mongodb --rm -e MONGO_USER="$MONGO_USER" -e MONGO_PASSWORD="$MONGO_PASSWORD" -e MONGO_DB="$MONGO_DB" MONGO
    export MONGO_HOST=$(docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' pgdb)
    mongo --host=$MONGO_HOST --port=$MONGO_PORT --username=$MONGO_USER $MONGO_DB

Then run the following commands to bootstrap your environment with ``pipenv``: ::

    git clone https://github.com/franloza/apiestas
    cd apiestas
    pipenv install
    pipenv shell

Then create ``.env`` file (or rename and modify ``.env.example``) in ``api`` or ``crawling`` folders and set environment variables for every application: ::

    cd api
    touch .env
    echo DB_CONNECTION=mongo://$MONGO_USER:$MONGO_PASSWORD@$MONGO_HOST:$MONGO_PORT/$MONGO_DB >> .env

To run the web application in debug use::

    python main.py api --reload


Development with Docker
-----------------------

You must have ``docker`` and ``docker-compose`` tools installed to work with material in this section. Then just run::

    docker-compose up -d

Application will be available on ``localhost`` or ``127.0.0.1`` in your browser.

Run tests with Docker
-----------------------
::

    docker-compose -f docker-compose-test.yml run tests


Web routes
----------

All routes are available on ``/docs`` or ``/redoc`` paths with Swagger or ReDoc.

Docs
#####

.. image:: img/docs.png

Redoc
#####

.. image:: img/redoc.png

Data sources
------------

Currently the application implements two working crawlers:
* ``oddsportalcom`` - Used as ground truth for matches and odds
* ``elcomparador.com`` - for odds data
* ``Codere`` - for odds data

TODO
----
1) Implement surebets calculation


