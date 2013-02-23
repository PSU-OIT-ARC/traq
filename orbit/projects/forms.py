from django import forms
from .models import Project, Component

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project

class ComponentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        project = kwargs.pop('project')
        super(ComponentForm, self).__init__(*args, **kwargs)
        self.instance.project = project
        if not self.is_bound:
            try:
                rank = Component.objects.order_by('-rank').all()[0].rank + 1
            except IndexError:
                rank = 1
            self.fields['rank'].initial = rank

    class Meta:
        model = Component
        exclude = ('project',)
