import re
from django import template
from django.http import QueryDict
from django.core.urlresolvers import resolve

register = template.Library()

QUOTES = "'\""

def build_variable(name):
    """
    Builds a ``template.Variable`` if unquoted, else returns the string
    unquoted.
    """
    if name[0] in QUOTES or name[-1] in QUOTES:
        if not name[-1] == name[0]:
            raise template.TemplateSyntaxError()
        return name[1:-1]
    return template.Variable(name)

def resolve_value(variable, context):
    """
    If given a ``template.Variable`` return the resolved value, otherwise
    return the given variable object.
    """
    if hasattr(variable, "resolve"):
        return variable.resolve(context)
    return variable

class QueryDictAppendNode(template.Node):
    def __init__(self, query_dict, key, values):
        self.query_dict = template.Variable(query_dict)
        self.key = build_variable(key)
        self.values = [build_variable(value) for value in values]

    def render(self, context):
        try:
            query_dict = self.query_dict.resolve(context)
            key = resolve_value(self.key, context)
        except template.VariableDoesNotExist:
            return u""
        for value in self.values:
            try:
                query_dict.appendlist(key, resolve_value(value, context))
            except template.VariableDoesNotExist:
                continue
        return u""

class QueryDictReplaceNode(template.Node):
    def __init__(self, query_dict, key, values):
        self.query_dict = template.Variable(query_dict)
        self.key = build_variable(key)
        self.values = [build_variable(value) for value in values]

    def render(self, context):
        try:
            query_dict = self.query_dict.resolve(context)
            key = resolve_value(self.key, context)
        except template.VariableDoesNotExist:
            return u""
        if key in query_dict:
            del query_dict[key]
        for value in self.values:
            try:
                query_dict.appendlist(key, resolve_value(value, context))
            except template.VariableDoesNotExist:
                continue
        return u""

class QueryDictDeleteKeyNode(template.Node):
    def __init__(self, query_dict, keys):
        self.query_dict = template.Variable(query_dict)
        self.keys = [build_variable(key) for key in keys]

    def render(self, context):
        query_dict = self.query_dict.resolve(context)
        for key in self.keys:
            try:
                key = resolve_value(key, context)
                del query_dict[key]
            except (KeyError, template.VariableDoesNotExist):
                continue
        return u""

class QueryDictUpdateNode(template.Node):
    def __init__(self, query_dict, others):
        self.query_dict = template.Variable(query_dict)
        self.others = [template.Variable(other) for other in others]

    def render(self, context):
        try:
            query_dict = self.query_dict.resolve(context)
        except template.VariableDoesNotExist:
            return u""
        for other in self.others:
            try:
                other = other.resolve(context)
                query_dict.update(other)
            except template.VariableDoesNotExist:
                continue
        return u""

class QueryDictCloneNode(template.Node):
    def __init__(self, query_dict, as_var):
        self.var = template.Variable(query_dict)
        self.as_var = build_variable(as_var)

    def render(self, context):
        try:
            query_dict = self.var.resolve(context)
            as_var = resolve_value(self.as_var, context)
            context[as_var] = query_dict.copy()
        except template.VariableDoesNotExist:
            pass
        return u""

class QueryDictNode(template.Node):
    def __init__(self, as_var):
        self.as_var = build_variable(as_var)

    def render(self, context):
        try:
            as_var = resolve_value(self.as_var, context)
            context[as_var] = QueryDict("", mutable=True)
        except template.VariableDoesNotExist:
            pass
        return u""

class QualifiedURLNode(template.Node):
    def __init__(self, path, as_var=None):
        self.path = build_variable(path)
        self.as_var = as_var

    def render(self, context):
        try:
            request = template.Variable("request").resolve(context)
            path = resolve_value(self.path)
        except template.VariableDoesNotExist:
            return u""
        url = request.build_absolute_uri(path)
        if self.as_url:
            context[self.as_var] = url
            return u""
        else:
            return url

class CurrentLocationNode(template.Node):
    def __init__(self, as_var):
        self.as_var = as_var

    def render(self, context):
        try:
            request = template.Variable("request").resolve(context)
        except template.VariableDoesNotExist:
            return u""
        url = request.path
        querystring = request.GET.urlencode()
        if querystring:
            url = "?".join([url, querystring])
        context[self.as_var] = url
        return u""


def compile_append_key(parser, token):
    """
    Appends one or more value(s) to the list of values for the given ``key``
    in the given ``QueryDict``.

    Usage::

        {% append_key <querydict> <key> [<value> ...] %}

    Note that the ``key`` and ``value`` arguments may be specified as template
    context variable names or quoted literals.
    """
    bits = token.split_contents()
    if not len(bits) > 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least three values: a querydict, a key, and one or more values to append" % bits[0]
        )
    query_dict = bits[1]
    key = bits[2]
    values = bits[3:]
    return QueryDictAppendNode(query_dict, key, values)

def compile_replace_key(parser, token):
    """
    Replaces the values for a given key in the given ``QueryDict`` with
    the given values. 

    Usage::

        {% replace_key <querydict> <key> [<value> ...] %}

    Note that ``key`` and each ``value`` may refer to other template context
    variables or be given as quoted literals.
    """
    bits = token.split_contents()
    if not len(bits) > 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least three values: a querydict, a key, and one or more values to set for the key" % bits[0]
        )
    query_dict = bits[1]
    key = bits[2]
    values = bits[3:]
    return QueryDictReplaceNode(query_dict, key, values)

def compile_delete_key(parser, token):
    """
    Removes the given ``key``(s) from the specified ``QueryDict``.

    Usage::

        {% delete_key <querydict> [<key> ...] %}

    Note that the ``key`` arguments may be specified as template context
    variables or as quoted literals.
    """
    bits = token.split_contents()
    if not len(bits) >= 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least two values: a querydict and one or more keys to delete" % bits[0]
        )
    query_dict = bits[1]
    keys = bits[2:]
    return QueryDictDeleteKeyNode(query_dict, keys)

def compile_update_query_dict(parser, token):
    """
    Updates the given ``QueryDict`` context variable with the values from
    the specified ``other`` context variables.

    Usage::

        {% update_query_dict <querydict> [<other> ...] %}

    """
    bits = token.split_contents()
    if not len(bits) >= 3:
        raise template.TemplateSyntaxError(
            "'%s' tag requires at least two values: a querydict to update and one or more dicts to merge" % bits[0]
        )
    query_dict = bits[1]
    others = bits[2:]
    return QueryDictUpdateNode(query_dict, others)

def compile_clone_query_dict(parser, token):
    """
    Clone the specified ``QueryDict`` template variable into a context
    variable specified by ``name``.

    Usage::
      
        {% clone_query_dict <querydict> as <name> %}
    
    """
    bits = token.split_contents()
    if not len(bits) == 4 or not bits[2] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: querydict variable, 'as', and a context variable name" % bits[0]
        )
    query_dict = bits[1]
    as_var = bits[3]
    return QueryDictCloneNode(query_dict, as_var)

def compile_query_dict(parser, token):
    """
    Creates a ``QueryDict`` in the context with the specified ``name``.

    Usage::

        {% query_dict as <name> %}

    """
    bits = token.split_contents()
    if not len(bits) == 3 or not bits[1] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: 'as', and a context variable name" % bits[0]
        )
    as_var = bits[2]
    return QueryDictNode(as_var)

def compile_current_location(parser, token):
    """
    Render the current URL path with querystring into a context variable.

    Usage::

        {% current_location as <name> %}

    """
    bits = token.split_contents()
    if not len(bits) == 3 or not bits[1] == u"as":
        raise template.TemplateSyntaxError(
            "'%s' tag must be called with the arguments: 'as', and a context variable name" % bits[0]
        )
    as_var = bits[2]
    return CurrentLocationNode(as_var)

@register.simple_tag(takes_context=True)
def active_nav(context, pattern):
        request = context['request']
        url_name = resolve(request.path).url_name
        if url_name == pattern:
            return 'active'
        return ''

register.tag("append_key", compile_append_key)
register.tag("replace_key", compile_replace_key)
register.tag("delete_key", compile_delete_key)
register.tag("update_query_dict", compile_update_query_dict)
register.tag("clone_query_dict", compile_clone_query_dict)
register.tag("query_dict", compile_query_dict)
register.tag("current_location", compile_current_location)
