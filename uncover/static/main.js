var submitInput = function() {
    $('#game-frame').html('<img src="static/loading.gif"/>');
    $.post('/by_username', {
            "username": $('#text-field').val()
    }).done(function(response) {
         console.log(response);
            $('#game-frame').empty();
         $.each(response, function(key, value){
            $('#game-frame').append("<img src=" + value + "/>");
         })
    }).fail(function() {
          $('#game-frame').text("error")
    })
};


$('#submit-btn').on('click' , submitInput);
$(document).on("submit", "#submit-form", submitInput)



