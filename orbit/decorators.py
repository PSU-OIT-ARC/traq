from django.core.exceptions import PermissionDenied

ARCSTAFF = "arcstaff"

class can_do(object):
    def __init__(self, model):
        self.model = model

    def check(self, request, user, model, pk):
        pass

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            request = args[0]
            try:
                pk = args[1]
            except IndexError:
                pk = None
            user = request.user
            if user.is_anonymous():
                raise PermissionDenied("No access")

            self.check(request, user, self.model, pk)

            return f(*args, **kwargs)

        return wrapper

class can_view(can_do):
    def check(self, request, user, model, pk):
        pass

class can_create(can_do):
    def check(self, request, user, model, pk):
        pass

class can_edit(can_do):
    def check(self, request, user, model, pk):
        if user.groups.filter(name=ARCSTAFF).exists():
            return

        try:
            model.objects.get(pk=pk, created_by=user)
        except model.DoesNotExist:
            raise PermissionDenied("No access")

