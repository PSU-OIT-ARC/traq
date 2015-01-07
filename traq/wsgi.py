import os
import site
import sys

prev_sys_path = list(sys.path)
root = os.path.normpath(os.path.join(os.path.dirname(__file__), "../"))
sys.path.append(root)
site.addsitedir(os.path.join(root, ".env/lib/python%d.%d/site-packages" % sys.version_info[:2]))
site.addsitedir(os.path.join(root, ".env/lib64/python%d.%d/site-packages" % sys.version_info[:2]))

# addsitedir adds its directories at the end, but we want our local stuff
# to take precedence over system-installed packages.
# See http://code.google.com/p/modwsgi/issues/detail?id=112
new_sys_path = []
for item in list(sys.path):
  if item not in prev_sys_path:
    new_sys_path.append(item)
    sys.path.remove(item)
sys.path[:0] = new_sys_path

os.environ.setdefault("DJANGO_SETTINGS_MODULE", os.path.basename(os.path.dirname(__file__)) + ".settings")


# This application object is used by any WSGI server configured to use this
# file. This includes Django's development server, if the WSGI_APPLICATION
# setting points here.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

# Apply WSGI middleware here.
# from helloworld.wsgi import HelloWorldApplication
# application = HelloWorldApplication(application)
