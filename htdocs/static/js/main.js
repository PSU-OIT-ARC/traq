$(document).ready(function(){
    $('.timestamp').each(function(el, i){
        // get rid of millseconds
        var d_string = $(this).text().replace(/\.\d+/, '');
        var d = new Date(d_string);
        var year = d.getFullYear();
        var month = d.getMonth() + 1;
        if(month < 10) month = "0" + month;
        var day = d.getDate();
        if(day < 10) day = "0" + day
        var hours = d.getHours();
        if(hours < 10) hours = "0" + hours
        var minutes = d.getMinutes();
        if(minutes < 10) minutes = "0" + minutes;
        var seconds = d.getSeconds();
        if(seconds < 10) seconds = "0" + seconds;
        //$(this).text(d.toLocaleString())
        $(this).text([year, month, day].join("-") + " " + [hours, minutes, seconds].join(":"))
    });
});
