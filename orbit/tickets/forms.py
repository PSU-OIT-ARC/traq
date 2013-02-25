from django import forms
from .models import Ticket, Comment, Work, TicketStatus, TicketPriority, WorkType

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

        # remove the blank choices from the fields
        self.fields['status'].empty_label = None
        self.fields['priority'].empty_label = None

        if not self.is_bound:
            self.fields['status'].initial = TicketStatus.objects.get(is_default=1)
            self.fields['priority'].initial = TicketPriority.objects.get(is_default=1)
            self.fields['component'].initial = project.defaultComponent()

        # a ticket doesn't neccessarily need to be assigned to anyone.
        # for some reason, you can't set this in the model field
        self.fields['assigned_to'].required = False
        self.fields['component'].required = False

    class Meta:
        model = Ticket
        exclude = ('project', 'created_by')

class QuickTicketForm(TicketForm):
    TIME_CHOICES = (
        ('00:30', '30m'),
        ('01:00', '1h'),
        ('01:30', '1h 30m'),
        ('02:00', '2h'),
        ('02:30', '2h 30m'),
        ('03:00', '3h'),
        ('03:30', '3h 30m'),
        ('04:00', '4h'),
        ('04:30', '4h 30m'),
        ('05:00', '5h'),
        ('05:30', '5h 30m'),
        ('06:00', '6h'),
        ('06:30', '6h 30m'),
        ('07:00', '7h'),
        ('07:30', '7h 30m'),
        ('08:00', '8h'),
    )
    estimated_time = forms.ChoiceField(choices=TIME_CHOICES)

    def __init__(self, *args, **kwargs):
        super(QuickTicketForm, self).__init__(*args, **kwargs)

    def save(self):
        body = self.instance.body
        max_length = self.fields['body'].max_length
        if len(body) > max_length:
            last_space = body.rfind(' ', 0, max_length)
            self.instance.title = body[0:last_space]
        else:
            self.instance.title = body

        super(QuickTicketForm, self).save()

    class Meta:
        model = Ticket
        exclude = ('project', 'created_by', 'title')
        widgets = {'body': forms.Textarea(attrs={'cols': 30})}

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

        self.fields['type'].empty_label = None
        if not self.is_bound:
            self.fields['type'].initial = WorkType.objects.get(is_default=1)


    class Meta:
        model = Work
        exclude = ('ticket', 'created_by')

