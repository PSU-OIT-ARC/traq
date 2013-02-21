from django import forms
from .models import Ticket, Comment
from ..projects.models import Attribute

class TicketForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        project = kwargs.pop("project")
        created_by = kwargs.pop("created_by")

        super(TicketForm, self).__init__(*args, **kwargs)

        # set the foreign key fields specified by the caller
        self.instance.project = project
        self.instance.created_by = created_by

        # add the choices for the enum fields
        self.fields['status'].queryset = Attribute.objects.asChoiceList('ticket_status')
        self.fields['status'].empty_label = None
        self.fields['priority'].queryset = Attribute.objects.asChoiceList('ticket_priority')
        self.fields['priority'].empty_label = None

        # a ticket doesn't neccessarily need to be assigned to anyone.
        # for some reason, you can't set this in the model field
        self.fields['assigned_to'].required = False

    class Meta:
        model = Ticket
        exclude = ('project', 'created_by')

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        created_by = kwargs.pop("created_by")
        ticket = kwargs.pop("ticket")

        super(CommentForm, self).__init__(*args, **kwargs)

        # set the foreign key fields specified by the caller
        self.instance.ticket = ticket
        self.instance.created_by = created_by

    class Meta:
        model = Comment
        exclude = ('ticket', 'created_by')
