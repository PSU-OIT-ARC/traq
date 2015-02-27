$(document).ready(function() {
    $('select').addClass('form-control');
    $("#id_filterset_form input,select").change(function() {
      $("#id_filterset_form").submit();
    });
    if($("#id_sprint_end").size()){
        select= $("#id_sprint_end");
        date = $("<input type='date' >").addClass('form-control').hide();
        cal = $("<div class='glyphicon glyphicon-calendar'></div>").css('padding-left','5px');
        close = $("<div class='glyphicon glyphicon-remove'></div>").css('padding-left','5px').hide();
        select.after(date);
        select.after(cal);
        date.after(close);
        cal.click(function(){handler(1);});
        close.click(function(){handler(0);});
        list = [];
        options = $('#id_sprint_end option');
        options.each(function(){
                list.push(this.value);
            });

        function handler(arg){
            select.toggle();
            cal.toggle();
            close.toggle();
            date.toggle();
            if(arg){
                select.attr('name','');
                date.attr('name','sprint_end');
            }else {
                date.attr('name','');
                select.attr('name','sprint_end');
                if($.inArray(date.val(), list) != -1){
                    select.val(date.val());
                }
            }
        }

        date.keypress(function(e){
            if(e.which == 13){
              $("#id_filterset_form").submit();
            }
        });

        if(DUE_PARAM){
           if($.inArray(DUE_PARAM,list ) == -1){
            cal.click();
            date.val(DUE_PARAM);
           }
        }
    }
});
