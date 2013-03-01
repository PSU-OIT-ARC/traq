import json
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.core.urlresolvers import reverse
from django.db import connection
from django.contrib import messages
from .forms import ProjectForm, ComponentForm
from .models import Project, Component
from ..tickets.models import Ticket
from ..tickets.forms import QuickTicketForm
from ..permissions.decorators import can_view, can_edit, can_create


