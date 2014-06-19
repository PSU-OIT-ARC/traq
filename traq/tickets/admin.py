from django.contrib import admin    
from traq.tickets.models import Ticket, TicketType, TicketStatus

admin.site.register(TicketType)
admin.site.register(TicketStatus)
