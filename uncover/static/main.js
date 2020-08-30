$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

/* main AJAX function */
const submitInput = function() {
    "use strict";
    // gets the desired method by the active button's id: (by_artist, by_username, by_spotify)
    const desired_method = $(".button.active").attr('id');
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
         /* adds a class 'loading' to block animation before all images are loaded */
         $('#game-frame').addClass('loading');
         var counter = 0;
         $.each(response["albums"], function(album_title, image_url){
            $('#game-frame').append($('<img>', {src:`${image_url}`, alt:`${album_title}`, id: `art-${counter}`}));
            counter++;
         });

          if ($('.button.active').attr('id') == 'by_artist') {
                $('#text-field').val(response["info"]);
           };
//         $('#text-field').val(response["info"]);
         // targets all images inside a #game-frame div, then gives them a 'cover-art' class
         $('#game-frame img').addClass('cover-art');

         $('#text-field').removeClass('is-invalid'); // restores a 'valid' form style
         $("#play-btn").show();

         /* waiting for all images to load before showing them up*/
          $('#game-frame').waitForImages().done(function() {
            $('#game-frame').removeClass('loading');
        });

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
                        "artist name");
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
  if ($('.button.active').attr('id') == 'by_username') {
    /* makes sure it's only visible for user's top albums */
    $("#select-options").show();
  };
}).focusout(function(){
    timerID = setTimeout(function() {
        $("#select-options").hide();
    }, 10);
});
