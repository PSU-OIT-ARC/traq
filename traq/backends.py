import ldap
from djangocas.backends import CASBackend
from django.contrib.auth.models import User, Group
from django.conf import settings as SETTINGS
from django.core.exceptions import PermissionDenied
from permissions import LOGIN_GROUPS

class PSUBackend(CASBackend):
    def get_or_init_user(self, username):
        # make sure this user is in the required group
        groups = self.get_groups(username)
        if set(groups) & set(LOGIN_GROUPS) == set():
            raise PermissionDenied("You need to belong to a group in LOGIN_GROUPS")

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()

        self.set_groups(user, groups)
        return user

    def set_groups(self, user, groups):
        for group in groups:
            group, created = Group.objects.get_or_create(name=group)
            user.groups.add(group)

    def get_groups(self, username):
        # figure out which ldap groups this user belongs to
        ld = ldap.initialize(SETTINGS.LDAP_URL)
        ld.simple_bind_s()
        results = ld.search_s(SETTINGS.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, "(& (memberUid=" + username + ") (cn=*))")
        groups = [result[1]['cn'][0] for result in results]
        try:
            user = User.objects.get(username=username)
            groups.extend([group.name for group in user.groups.all()])
        except User.DoesNotExist:
            pass

        return groups

