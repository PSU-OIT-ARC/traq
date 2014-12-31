# Install
## Requirements

To build `python-ldap` with pip on centos, you need the `openldap24-libs-devel` package.

    yum install openldap24-libs-devel

And when you install python-ldap with pip, you need to set these envars:

    export CPATH=/usr/include/openldap24
    export LIBRARY_PATH=/usr/lib/openldap24/

Create a virtual environment, and install the required packages in it:

    virtualenv --no-site-packages -p python3 .env
    source .env/bin/activate
    make install

## Settings
Create a settings file from the template, and fill in the blanks:

    cp traq/demo_settings.py traq/local_settings.py
    vim traq/local_settings.py

## Databases
To update/recreate the database

    make recreate-db

## Media
Create the media upload dir (for user files)

    mkdir htdocs/media
    # make the dir world writeable
    # or make apache the owner of the dir
    chown apache htdocs/media || chmod 1777 htdocs/media

## Run
Run the server

    make
