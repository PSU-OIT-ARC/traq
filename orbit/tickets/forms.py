from django import forms
from .models import Ticket, Comment, Work
from ..projects.models import Attribute, AttributeTypeName

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
        self.fields['status'].queryset = Attribute.objects.ofType(AttributeTypeName.TICKET_STATUS)
        self.fields['status'].empty_label = None
        self.fields['priority'].queryset = Attribute.objects.ofType(AttributeTypeName.TICKET_PRIORITY)
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

class WorkForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        # these fields won't appear on the form; they need to be specified by
        # the caller
        ticket = kwargs.pop("ticket")
        created_by = kwargs.pop("created_by")

        super(WorkForm, self).__init__(*args, **kwargs)

        self.instance.ticket = ticket
        self.instance.created_by = created_by

        self.fields['type'].queryset = Attribute.objects.ofType(AttributeTypeName.WORK_TYPE)
        self.fields['type'].empty_label = None

    class Meta:
        model = Work
        exclude = ('ticket', 'created_by')

