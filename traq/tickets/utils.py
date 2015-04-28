from django.shortcuts import get_object_or_404
from .models import Ticket

def get_user_ticket(user_id, ticket_id, index_difference):
    """
    Gets a list of tickets assigned to a user, finds the index of the current ticket, then returns the ticket in the relative position given by index_difference
    e.g. To get a the ticket assigned to user 1, directly after ticket #34, the call would look like

        get_user_ticket(1, 34, 1)

    Likewise, to get the previous ticket,

        get_user_ticket(1, 34, -1)

    """
    current = get_object_or_404(Ticket, pk=ticket_id)
    tickets = list(Ticket.objects.filter(assigned_to_id=user_id))
    try:
        current_index = tickets.index(current)
    except ValueError as e:
        # currently looking at someone elses tickets.
        # Gonna get sent back to your first ticket
        current_index = 0
    length = len(tickets)
    new_index = current_index + index_difference
    try:
        return tickets[new_index % length]
    except ZeroDivisionError as e:
        return None

