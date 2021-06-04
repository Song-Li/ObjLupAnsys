function upload_file() {
  $("#readyimg").remove();
  var form_data = new FormData($('#uploadfile')[0]);
  $.ajax({
    url: '/upload',
    type: 'POST',
    data: form_data,
    contentType: false,
    cache: false,
    processData: false,
    success: function(data){
      $("#uploaditems").append('<img id="readyimg" class="img" src="/imgs/ok.gif"/>');
    }
  });
}

function check_progress() {
  var id = setInterval(frame, 100);
  function frame() {
    $.ajax({
      url: '/progress',
      type: 'GET',
      success: function(data){
        if (data >= 100) clearInterval(id)
        if ($('#progress').val() >= 100) return ;
        $('#progress').val(20 * data);
      }
    });
  }
  return id;
}

function start_check() {
  $('#progress').val(0);
  progress_id = check_progress(0, 0);
  $.ajax({
    url: '/check',
    type: 'POST',
    data: $('#options').serialize(),
    success: function(data){
      clearInterval(progress_id);
      if (data == "Not detected") {
        $("#cy").html(data);
      } else {
        eval(data);
      }
      $('#progress').val(100);
    }
  });
}
