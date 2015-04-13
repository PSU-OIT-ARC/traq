$(document).ready(function() {
          $('select[multiple="multiple"]').multiselect({
              nonSelectedText: '--------'
              });
    if($('select[multiple="multiple"] option:selected').length > 2){
      $('.multiselect').after('<button class="btn btn-default" id="deselect-all">&times;</button>');
    }
    $('#deselect-all').on('click', function() {
        $('#id_status').multiselect('deselectAll', false);
        $('#id_status').multiselect('updateButtonText');
    });
});
