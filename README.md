# Install
## Environment
Create a virtual environment, and install the required packages in it:

    virtualenv-2.6 --no-site-packages .env
    source .env/bin/activate
    pip install -r requirements.txt

## Settings
Create a settings file from the template, and fill in the blanks:

    cp orbit/demo_settings.py orbit/local_settings.py
    vim orbit/local_settings.py
