#thanks to https://github.com/iivvoo
from django import template
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter(name='addcss')
def addclass(field, css):
    return field.as_widget(attrs={"class":css})

@register.filter(name='addattr')
def addattr(field, args):
    if args is None:
        return false
    arg_list=[arg.strip() for arg in args.split(',')]
    return field.as_widget(attrs={arg_list[0]:arg_list[1]})

@register.filter(name='bs_group')
def bootstrap(field, column):
    '''returns bootstrap form-group markup with a given column width. 
       usage: {{ form.field | bs_group:'4' }}'''
    classes = field.field.widget.attrs.get('class','')
    field.field.widget.attrs["class"] = "%s form-control" % classes
    return mark_safe('<div class="form-group col-md-%s"><label>%s</label>%s</div>' % (column, field.label, field))
