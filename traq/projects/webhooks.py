"""
A simplified and naive implementation of webhook receivers.
"""
import os, os.path
import subprocess
import logging
import shlex

logger = logging.getLogger(__name__)


class WebhookReceiver(object):
    """
    TBD
    """
    PROJECT_ROOT = '/vol/www'
    
    def __init__(self, payload):
        self.payload = payload

    def run(self):
        raise NotImplementedError

class WebhookPushReceiver(WebhookReceiver):
    """
    TBD
    """
    enabled_projects = ['cdn']
    cmds = ['git fetch origin', 'git pull origin']

    def run(self):
        try:
            repository = self.payload.get('repository')
            path = os.path.join(self.PROJECT_ROOT, repository.get('name'))
            os.chdir(path)
        except IOError as e:
            logger.error("Could not change directory to: '%s'" % (path))
            return

        try:
            for cmd in self.cmds:
                subprocess.check_call(shlex.split(cmd))
        except subprocess.CalledProcessError as e:
            logger.error("Error while updating git repository: '%s'" % (e))

def validate_webhook(request):
    """
    Using pre-shared secret we can compare the HMAC has provided in
    the HTTP header X-Hub-Signature to validate the source of this
    request.
    """
    return True

def handle_webhook(request, payload):
    """
    TBD
    """
    if not validate_webhook(request):
        logger.error("Webhook failed to validate: %s (%s)" % (request, payload))

    event_name = request.META.get('HTTP_X_GITHUB_EVENT')
    if event_name == 'push':
        logger.info("Received 'ping' event with payload: %s" % (payload))
        handler = WebhookPushReceiver(payload)
        handler.run()
    elif event_name == 'ping':
        logger.info("Received 'ping' event with payload: %s" % (payload))
        handler = WebhookPushReceiver(payload)
        handler.run()
