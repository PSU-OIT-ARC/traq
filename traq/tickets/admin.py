from django.contrib import admin    
from traq.tickets.models import Ticket, TicketType, TicketStatus, WorkType

admin.site.register(TicketType)
admin.site.register(TicketStatus)
admin.site.register(WorkType)
