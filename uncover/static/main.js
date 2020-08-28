/* main AJAX function */
var submitInput = function() {
    // gets the desired method by the active button's id: (by_artist, by_username, by_spotify)
    desired_method = $(".button.active").attr('id');
    // spinner
    $('#game-frame').html('<img src="static/images/loading/broken-1.1s-47px.gif"/>');
    // posts to the flask's route /by_username
    $.post(`/${desired_method}`, {
            "qualifier": $('#text-field').val(),
            "option": $('#select-options').val()
    }).done(function(response) {
         // when done, removes current pictures from the frame, adds new ones
         console.log(response);

         $('#game-frame').empty();
         $.each(response["albums"], function(album_title, image_url){
            $('#game-frame').append($('<img>', {src:`${image_url}`, alt:`${album_title}`}));
         });

         $('#text-field').val(response["info"]);

         $('img').addClass('cover-art');

         $('#text-field').removeClass('is-invalid'); // restores a 'valid' form style
    }).fail(function(response) {
            console.log(response.responseJSON);
          $('#text-field').addClass('is-invalid').val(response.responseJSON['message']); // show error message
          $('#game-frame').html(`
                <img src="${response.responseJSON['failure_art']}" id="failure-art"/>
                <div class="text-block">
                    <h1 class="text-light">someone made an oopsie!</h1>

                </div>
          `);
    })
};



//$('#submit-btn').on('click' , submitInput);
$(document).on("submit", "#submit-form", submitInput);

/* 'activates' buttons */
$('.button').on('click', function(){
    $('.button').removeClass('active');
    $(this).addClass('active');

    if ($('.button.active').attr('id') == 'by_username') {
    $('#text-field').attr('placeholder', 'last.fm username');
} else if ($('.button.active').attr('id') == 'by_artist') {
     $('#text-field').attr(
                        'placeholder',
                        "artist/band/group (e.g. Arcade Fire, David Bowie or MGMT)");
} else {
     $('#text-field').attr(
                        'placeholder',
                        "Spotify Playlist Link");
};
$('#text-field').val('');
});

/* displays 'options' menu when the input's focused  */
var timerID;
$("#text-field, #select-options").focus(function() {
  clearTimeout(timerID);
  $("#select-options").show();
}).focusout(function(){
    timerID = setTimeout(function() {
        $("#select-options").hide();
    }, 10);
});
