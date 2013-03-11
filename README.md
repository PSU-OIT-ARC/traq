# Install
## Environment

To build `python-ldap` with pip on centos, you need the `openldap24-libs-devel` package.

    yum install openldap24-libs-devel

And when you install python-ldap with pip, you need to set these envars:
    
    export CPATH=/usr/include/openldap24
    export LIBRARY_PATH=/usr/lib/openldap24/

Create a virtual environment, and install the required packages in it:

    virtualenv-2.6 --no-site-packages .env
    source .env/bin/activate
    pip install -r requirements.txt

## Settings
Create a settings file from the template, and fill in the blanks:

    cp orbit/demo_settings.py orbit/local_settings.py
    vim orbit/local_settings.py
