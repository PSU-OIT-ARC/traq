# Install
## Requirements

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

## Test
To test the site, use either

    make test

Or
    
    make coverage
