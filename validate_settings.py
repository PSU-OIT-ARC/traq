import StringIO
import os.path

from django.core.management import call_command
from django.conf import settings


def validate_secret_key():
    print "You have not configured 'SECRET_KEY'."
    print "Generating a suitable value and placing it in 'local_settings.py'."

    output = StringIO.StringIO()
    call_command('generate_secret_key', stdout=output)
    output.seek(0)
    secret_key = output.read().strip()

    with open(os.path.join(settings.PROJECT_DIR, 'local_settings.py'), 'a') as f:
        f.write("\nSECRET_KEY=\"%s\"\n" % (secret_key))

def main():
    if settings.SECRET_KEY == 'changeme':
        validate_secret_key()
