$(document).ready(function(){
    $('#ticket-search').bind('keyup', function(e){
        if(e.keyCode == 13){ // user hit enter key
            window.location = $('#ticket-list tbody tr:visible a:first').attr('href');
        }
        var needles = $(this).val().toLowerCase().split(/\s+/g)
        // for each ticket
        for(var i = 0; i < TICKETS.length; i++){
            var ticket = TICKETS[i];
            // add a property to the ticket so the user can type "#<ticket_id>"
            // and jump right to the ticket
            ticket.id = "#" + ticket.ticket_id

            var elements = $('#t1-' + ticket.ticket_id + ", #t2-" + ticket.ticket_id);
            elements.hide();
            // keep track of how many needles were found
            var found_needles = 0;
            // try to find all the needles in this ticket
            for(var j = 0; j < needles.length; j++){
                var needle = needles[j];
                // search all the fields of this ticket for the needle
                for(var k in ticket){
                    var haystack = ticket[k];
                    if(haystack == null) continue;
                    // found the needle?
                    if(haystack.toString().toLowerCase().indexOf(needles[j]) != -1){
                        found_needles++;
                        break;
                    }
                }
            }
            // if we found all the needles, then this ticket matches our search
            // term
            if(found_needles == needles.length){
                elements.show();
            }
        }
    });
})
