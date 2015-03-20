[![Build Status](https://travis-ci.org/PSU-OIT-ARC/traq.svg?branch=master)](https://travis-ci.org/PSU-OIT-ARC/traq)

# Install

## Full Install and Setup
If you want to install requirements, create a local db and load
some dummy data, and run tests all at once just run:

    make init

## Minimal Install and Setup (for production)

    make install

## Databases
To update/recreate the database

    make recreate-db

## Dummy Data
To load some dummy projects and tickets

    make load-dev-data

## Media
Create the media upload dir (for user files)

    mkdir htdocs/media
    # make the dir world writeable
    # or make apache the owner of the dir
    chown apache htdocs/media || chmod 1777 htdocs/media

## Run
Run the server

    make

## Test
To test the site, use either

    make test

Or

    make coverage

Then go to http://<host|ip>:port/htmlcov/index.html for the report
