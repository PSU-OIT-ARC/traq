from arcutils import ldap

from django.conf import settings
from django.core.exceptions import PermissionDenied
from django.contrib.auth.models import User, Group

from arcutils.cas.backends import CASModelBackend

from .permissions import LOGIN_GROUPS


class PSUBackend(CASModelBackend):

    def authenticate(self, ticket, service):
        user = super(PSUBackend, self).authenticate(ticket, service)

        if user is not None:
            username = user.username
            groups = self.get_groups(username)
            in_a_login_group = bool(set(groups).intersection(LOGIN_GROUPS))
            if not in_a_login_group:
                raise PermissionDenied('You need to belong to a group in LOGIN_GROUPS')
            self.set_groups(user, groups)

        return user

    def set_groups(self, user, groups):
        for group in groups:
            group, created = Group.objects.get_or_create(name=group)
            user.groups.add(group)

    def get_groups(self, username):
        if settings.DEBUG and settings.LDAP_DISABLED:
            return LOGIN_GROUPS

        results = ldap.ldapsearch('(& (memberUid=' + username + ') (cn=*))')
        groups = [result[1]['cn'][0] for result in results]

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        else:
            groups.extend([group.name for group in user.groups.all()])

        return groups
