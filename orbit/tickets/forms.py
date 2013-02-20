from django import forms
from .models import Ticket
from ..projects.models import Attribute

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # set the project foreign key on the form instance
        # since it is excluded in the meta
        project = kwargs.pop("project")
        super(TicketForm, self).__init__(*args, **kwargs)
        self.fields['status'].queryset = Attribute.objects.asChoiceList('ticket_status')   
        self.instance.project = project

    class Meta:
        model = Ticket
        exclude = ('project', )
