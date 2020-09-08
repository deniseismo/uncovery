$(document).ready(function(){
  $('[data-toggle="tooltip"]').tooltip();
});

let albums;

/* main AJAX function */
const submitInput = function() {
    "use strict";
    $('#info').remove();
    $('#play-button').removeClass('visible');
    // gets the desired method by the active button's id: (by_artist, by_username, by_spotify)
    const desiredMethod = $(".method.active").attr('id');
    // spinner
    $('#game-frame').html('<img src="static/images/loading/broken-1.1s-47px.gif"/>');
    // posts to the flask's route /by_username
    $.post(`/${desiredMethod}`, {
            "qualifier": $('#text-field').val(),
            "option": $('#select-options').val()
    }).done(function(response) {
        // when done, removes current pictures from the frame, adds new ones
        console.log(response);
        /* storing album info in a global object */
        albums = response['albums'];

        $('#game-frame').empty();
        /* adds a class 'loading' to block animation before all images are loaded */
        $('#game-frame').addClass('loading');

        /* main iteration */
        const totalAmountOfAlbums = response['albums'].length;
        let length = (totalAmountOfAlbums < 10) ? totalAmountOfAlbums : 9;
        for (var i = 0; i < length; i++) {
            let album = response['albums'][i];
            let title = response['albums'][i]['title'];
            let imageURL = response['albums'][i]['image'];
            let id = response['albums'][i]['id']

            let img = $('<img />').attr({
                'id': `art-${id}`,
                'src': `${imageURL}`,
                'alt': `${title}`,
            })
            $('<div />', {class: 'flex-item', id: `item-${i}`})
                .wrapInner(img).appendTo("#game-frame");
        }

        if ($('.button.active').attr('id') == 'by_artist') {
            $('#text-field').val(response["info"]);
        };
        // $('#text-field').val(response["info"]);
        // targets all images inside a #game-frame div, then gives them a 'cover-art' class
        $('#game-frame img').addClass('cover-art');
        $('#text-field').removeClass('is-invalid'); // restores a 'valid' form style

        /* add a progress bar */
        $('#buttons-container').after($('<div>', {id: 'load-bar'}));
        /* waiting for all images to load before showing them up*/
        $('#game-frame').waitForImages(function() {
        /* remove progress bar once loaded */
            $('#load-bar').remove();
         /* remove 'loading' class that blocks animation of albums images */
            $('#game-frame').removeClass('loading');

            $('#play-button').addClass('visible');
            if ($('.button.active').attr('id') == 'by_username' || $('.button.active').attr('id') == 'by_spotify') {
                $('#game-frame').after(`<div id="info">${response["info"]}</div>`);
            };
        }, function(loaded, count, success) {
        /* animate progress bar */
             var bar1 = new ldBar("#load-bar", {
                 'preset': 'line'
             });
             bar1.set((loaded + 1 / count) * 100);
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

/* play button */
$("#play-button").on('click', function() {
    console.log(albums);
    $(this).toggleClass('on off');

    if($(this).hasClass('on')) {
        $('#text-field')
                        .attr('id', 'play-field')
                        .attr('placeholder', 'try guessing the albums')
                        .val('');
        $("#select-options").hide();
        $(".method").hide();
        $(this).val('GIVE UP');
        $('#ok-btn').hide();
        let input = document.querySelector('#play-field');
        input.oninput = handleInput;
    }
    else {
        $('#play-field')
                        .attr('id', 'text-field')
                        .val('');
        $(".method").show();
        $(this).val('PLAY');
        $('#ok-btn').show();
    };
});


function handleInput(e) {
    // TODO: handle guessing the albums
    const options = {
    // isCaseSensitive: false,
    // includeScore: false,
    // shouldSort: true,
    // includeMatches: false,
    // findAllMatches: false,
    minMatchCharLength: 12,
    location: 2,
    threshold: 0.03,
    // distance: 100,
    // useExtendedSearch: false,
    // ignoreLocation: false,
    // ignoreFieldNorm: false,
    keys: [
    "names",
     ]
    };
  const fuse = new Fuse(albums, options);
  const pattern = e.target.value;
  if (fuse.search(pattern).length > 0) {
    let id = fuse.search(pattern)[0]['item']['id'];
    console.log(id);
    console.log(pattern);
    console.log(`search results: ${fuse.search(pattern)[0]['item']['title']}`);
    $(`#art-${id}`).addClass('guessed-right');
  }
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
$("#text-field, #select-options").focusin(function() {
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
