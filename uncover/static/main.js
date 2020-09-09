// main global object with all the info about albums & album covers
let albums;
/* main AJAX function */
const submitInput = function() {
    "use strict";
    // make 'play-button' disappear
    const playButton = document.querySelector("#play-button");
    playButton.classList.remove("visible");
    // make info at the bottom disappear
    const responseInfo = document.querySelector("#response-info");
    if (responseInfo) {
        responseInfo.remove();
    };
    // gets the desired method by the active button's id: (by_artist, by_username, by_spotify)
    const desiredMethod = $(".method.active").attr('id');
    const gameFrame = document.querySelector("#game-frame");
    // empty html
    removeAllChildNodes(gameFrame);
    // add spinner while waiting for the response
    loadSpinner(gameFrame);
    // posts to the flask's route /by_username
    $.post(`/${desiredMethod}`, {
            "qualifier": $('#text-field').val(),
            "option": $('#select-options').val()
    }).done(function(response) {
        /* storing album info in a global object */
        albums = response['albums'];
        // restores a 'valid' form style
        const textField = document.querySelector("#text-field");
        textField.classList.remove("is-invalid");
        // when done, removes current pictures from the frame, adds new ones
        console.log(response);
        const gameFrame = document.querySelector("#game-frame");
        // empty html
        removeAllChildNodes(gameFrame);
        /* adds a class 'loading' to block animation before all images are loaded */
        gameFrame.classList.add('loading');
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

        /* add a progress bar */
        $('#buttons-container').after($('<div>', {id: 'load-bar'}));
        /* waiting for all images to load before showing them up*/
        $('#game-frame').waitForImages(function() {
        /* remove progress bar once loaded */
            $('#load-bar').remove();
         /* remove 'loading' class that blocks animation of albums images */
            const gameFrame = document.querySelector("#game-frame");
            gameFrame.classList.remove("loading");

            const playButton = document.querySelector("#play-button");
            playButton.classList.add("visible");

            if ($('.button.active').attr('id') == 'by_username' || $('.button.active').attr('id') == 'by_spotify') {
                $('#game-frame').after(`<div id="response-info">${response["info"]}</div>`);
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

          const textField = document.querySelector("#text-field");
          textField.classList.add("is-invalid");
          //val(response.responseJSON['message']); // show error message
          const gameFrame = document.querySelector("#game-frame");
          const failureArtURL = response.responseJSON['failure_art'];

          removeAllChildNodes(gameFrame);
          loadFailureArt(gameFrame, failureArtURL);
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
        input.oninput = handleGuesses;
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


function handleGuesses(e) {
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


function loadFailureArt(node, url) {
    console.log(this);
    const failureArt = document.createElement("img");
    failureArt.src = url;
    failureArt.id = "failure-art";

    const failureArtBlock = document.createElement("div");
    failureArtBlock.classList.add("failure-art-block");

    const failureArtText = document.createElement("h1");
    failureArtText.classList.add("text-light")
    failureArtText.textContent = "someone made an oopsie!"

    failureArtBlock.appendChild(failureArtText);

    node.appendChild(failureArt);
    node.appendChild(failureArtBlock);
};


function loadSpinner(node) {
    const spinner = document.createElement("img");
    const url = "static/images/loading/broken-1.1s-47px.gif"
    spinner.src = url;
    node.appendChild(spinner);
};


function removeAllChildNodes(parent) {
    while (parent.firstChild) {
        parent.removeChild(parent.firstChild);
    }
};

/* tooltips */
// find all elements that need tooltips
const tooltipElements = document.querySelectorAll('.info-tooltip')
// loop through every such element
tooltipElements.forEach(function(el) {
    // add 'label' element
    const tooltip = document.createElement('label');
    // add class to it
    tooltip.classList.add('tooltipText');
    // change text of that element to the text from 'data-tooltip' of the element
    tooltip.innerHTML = el.dataset.tooltip;
    el.appendChild(tooltip);
});
