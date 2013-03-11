import ldap
from django_cas.backends import CASBackend
from django.contrib.auth.models import User, Group
from django.conf import settings as SETTINGS

class PSUBackend(CASBackend):
    def get_or_init_user(self, username):
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            # user will have an "unusable" password
            user = User.objects.create_user(username, '')
            user.save()

        self.set_groups(user)
        # get all the groups
        return user

    def set_groups(self, user):
        ld = ldap.initialize(SETTINGS.LDAP_URL)
        ld.simple_bind_s()
        results = ld.search_s(SETTINGS.LDAP_BASE_DN, ldap.SCOPE_SUBTREE, "(& (memberUid=" + user.username + ") (cn=*))")
        groups = [result[1]['cn'][0] for result in results]
        for group in groups:
            group, created = Group.objects.get_or_create(name=group)
            user.groups.add(group)


