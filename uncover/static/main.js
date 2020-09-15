// main global object with all the info about albums & album covers
let albums;
let notGuessedAlbums;
// a global variable that stores a number of albums guessed so far
let guessedCount = 0;
/* main AJAX function */

const frequentElements = {
    gameFrame: document.querySelector('#game-frame'),
    playButton: document.querySelector('#play-button'),
    textField: document.querySelector('#text-field')
};

const submitInput = function() {
    "use strict";
    // make 'play-button' disappear
    frequentElements.playButton.classList.remove("visible");
    // make info at the bottom disappear (if exists)
    const responseInfo = document.querySelector(".data-info");
    if (responseInfo) {
        responseInfo.remove();
    };
    // gets the desired method by the active button's id: (by_artist, by_username, by_spotify)
    const desiredMethod = document.querySelector('.method.active').id;
    frequentElements.gameFrame.classList.remove('shadow-main');
    // empty html
    removeAllChildNodes(frequentElements.gameFrame);
    // add spinner while waiting for the response
    loadSpinner(frequentElements.gameFrame);
    // posts to the flask's route /by_username
    fetch(`${desiredMethod}`, {
        method: 'POST',
        headers: new Headers({
            'Content-Type': 'application/json'
        }),
        body: JSON.stringify({
            "qualifier": document.querySelector('#text-field').value,
            "option": document.querySelector('.select-options').value
        })
    }).then(response => {
        // if response is not ok (status ain't no 200)
        if (!response.ok) {
            // we get json with the 'failure' info
            const waves = document.querySelectorAll('.wave');
            waves.forEach(wave => wave.classList.add('falldown'));
            return response.json()
                .then(failData => {
                    frequentElements.textField.classList.add("is-invalid");
                    //val(failData.failDataJSON['message']); // show error message
                    removeAllChildNodes(frequentElements.gameFrame);
                    loadFailureArt(frequentElements.gameFrame, failData);
                });
        }

        return response.json();

    }).then(data => {
        /* storing album info in a global object */
        albums = data['albums'];
        notGuessedAlbums = albums.slice(0, 10);
        // restores a 'valid' form style
        frequentElements.textField.classList.remove("is-invalid");
        // when done, removes current pictures from the frame, adds new ones
        console.log(data);
        // empty html
        removeAllChildNodes(frequentElements.gameFrame);
        /* adds a class 'loading' to block animation before all images are loaded */
        frequentElements.gameFrame.classList.add('loading');
        /* load/add cover art images */
        loadCoverArt(data);
        fixArtistName(data);
        // $('#text-field').val(data["info"]);
        /* add a progress bar */
        const progressBar = document.createElement("div");
        progressBar.id = "progress-bar";
        const referenceNode = document.querySelector("#buttons-container");
        referenceNode.after(progressBar);
        const waves = document.querySelectorAll('.wave');
        waves.forEach(wave => wave.classList.add('falldown'));
        /* waiting for all images to load before showing them up*/
        $('#game-frame').waitForImages(function() {
            /* remove progress bar once loaded */
            console.log(this);
            progressBar.remove();
            /* remove 'loading' class that blocks animation of albums images */
            this.classList.remove("loading");
            const itemsList = document.querySelectorAll(".flex-item");
            itemsList.forEach(item => {
                item.classList.add("loaded");
            });

            frequentElements.playButton.classList.add("visible");

/*            if ($('.button.active').attr('id') == 'by_username' || $('.button.active').attr('id') == 'by_spotify') {
                $('#game-frame').after(`<class="data-info">${data["info"]}</div>`);
            };*/
        }, function(loaded, count, success) {
            /* animate progress bar */
            var bar1 = new ldBar("#progress-bar", {
                'preset': 'line'
            });
            bar1.set((loaded + 1 / count) * 100);
        });
    }).catch((error) => {
        // Handle the error
        console.log(`error is ${error}`);
    });
};

// event listener for a submit form and an 'ok' submit button
const submitForm = document.querySelector('#submit-form');
submitForm.addEventListener('submit', submitInput);

// play button
frequentElements.playButton.onclick = (e) => {
    // reset score, remove 'success' icons
    resetGame();
    e.target.classList.toggle('on');
    if (e.target.classList.contains('on')) {
        prepareGame();
        const input = document.querySelector('#play-field');
        input.oninput = handleGuesses;
    } else {
        cancelGame();
    };
};


function handleGuesses(e) {
    "use strict";
    // TODO: handle guessing the albums
    const options = {
        // isCaseSensitive: false,
        // includeScore: false,
        // shouldSort: true,
        // includeMatches: false,
        // findAllMatches: false,
        minMatchCharLength: 12,
        location: 2,
        threshold: 0.015,
        // distance: 100,
        // useExtendedSearch: false,
        // ignoreLocation: false,
        // ignoreFieldNorm: false,
        keys: [
            "names",
        ]
    };
    const fuse = new Fuse(notGuessedAlbums, options);
    const pattern = e.target.value;
    if (fuse.search(pattern).length > 0) {
        let id = fuse.search(pattern)[0]['item']['id'];
        console.log(`search results: ${fuse.search(pattern)[0]['item']['title']}`);
        const guessedAlbum = document.querySelector(`.art-${id}`);
        const title = albums[id]['title'];
        guessedAlbum.classList.add("guessed-right");
        guessedAlbum.alt = title;
        const successIcon = document.querySelector(`#success-${id}`);
        successIcon.classList.add('visible');
        const totalAmountOfAlbums = albums.length;
        const total = Math.min(totalAmountOfAlbums, 9);
        guessedCount++;
        const scoreText = document.querySelector(".score-text");
        scoreText.textContent = `Wowee! You've guessed ${guessedCount} out of ${total}.`;
        removeGuessedAlbum(id);
    }
};

// activate buttons
const buttonsContainer = document.querySelector('#buttons-container');
// add an event listener to a buttons wrapper (event bubbling)
buttonsContainer.addEventListener('click', (event) => {
    const isButton = event.target.nodeName === 'INPUT';
    // check if a button was clicked, not the div
    if (!isButton) {
        return;
    };
    const methodButtonsList = document.querySelectorAll(".method");
    methodButtonsList.forEach(button => button.classList.remove('active'));
    event.target.classList.add('active');
    // change placeholder to a correct one
    setPlaceholder();
    frequentElements.textField.value = '';
});

/* displays 'options' menu when the input's focused  */
var timerID;
$("#text-field, .select-options").focusin(function() {
    clearTimeout(timerID);
    if ($('.button.active').attr('id') == 'by_username' && !$('#play-button').hasClass("on")) {
        /* makes sure it's only visible for user's top albums */
        $(".select-options").show();
    };
}).focusout(function() {
    timerID = setTimeout(function() {
        $(".select-options").hide();
    }, 10);
});

function fixArtistName(data) {
    const activeButtonID = document.querySelector('.button.active').id;
    if (activeButtonID === 'by_artist') {
        frequentElements.textField.value = data['info'];
    };
};


function loadCoverArt(data) {
    "use strict";
    const totalAmountOfAlbums = data['albums'].length;
    let length = (totalAmountOfAlbums < 10) ? totalAmountOfAlbums : 9;
    for (var i = 0; i < length; i++) {
        const album = data['albums'][i];
        const imageURL = data['albums'][i]['image'];
        const id = data['albums'][i]['id']
        const coverArt = document.createElement("img");
        coverArt.classList.add(`art-${id}`);
        coverArt.classList.add('cover-art');
        coverArt.src = `${imageURL}`;
        const successIcon = document.createElement('img');
        successIcon.id = `success-${id}`;
        successIcon.classList.add('success-icon');
        successIcon.src = 'static/images/check-mark-contrast.png';
        successIcon.alt = 'checkmark';
        const flexItem = document.createElement('div');
        flexItem.id = `item-${i}`;
        flexItem.classList.add('flex-item');
        flexItem.appendChild(coverArt);
        flexItem.appendChild(successIcon);
        frequentElements.gameFrame.appendChild(flexItem);
    }
};

function removeGuessedAlbum(albumID) {
    "use strict";
    for (let i = 0; i < notGuessedAlbums.length; i++) {
        if (notGuessedAlbums[i]['id'] === albumID) {
            notGuessedAlbums.splice(i, 1);
            return true;
        }
    }
}

function setPlaceholder() {
    "use strict";
    const activeButtonID = document.querySelector('.button.active').id;
    if (activeButtonID === 'by_username') {
        frequentElements.textField.placeholder = 'last.fm username';
    } else if (activeButtonID === 'by_artist') {
        frequentElements.textField.placeholder = 'artist name';
    } else {
        frequentElements.textField.placeholder = 'Spotify Playlist Link';
    };
}

function prepareGame() {
    "use strict";
    const scoreContainer = document.querySelector('.score-container');
    frequentElements.textField.id = 'play-field';
    frequentElements.textField.placeholder = 'try guessing the albums';
    frequentElements.textField.value = ''
    const submitForm = document.querySelector("#submit-form");
    submitForm.id = 'guess-form';
    const selectOptions = document.querySelector(".select-options");
    selectOptions.style.display = 'none';
    const methodButtonsList = document.querySelectorAll(".method");
    methodButtonsList.forEach(button => button.style.display = 'none');
    scoreContainer.style.display = "block";
    const scoreText = document.querySelector(".score-text");
    scoreText.textContent = "You haven't guessed any albums yet. 😟"
    frequentElements.playButton.value = 'GIVE UP';
    const okButton = document.querySelector(".ok-btn");
    okButton.style.display = "none";
};

function cancelGame() {
    "use strict";
    const scoreContainer = document.querySelector('.score-container');
    scoreContainer.style.display = "none";
    const playField = document.querySelector("#play-field");
    playField.id = 'text-field';
    playField.placeholder = '';
    playField.value = ''
    const guessForm = document.querySelector("#guess-form");
    guessForm.id = 'submit-form';
    const methodButtonsList = document.querySelectorAll(".method");
    methodButtonsList.forEach(button => button.style.display = 'block');
    frequentElements.playButton.value = 'PLAY';
    const okButton = document.querySelector(".ok-btn");
    okButton.style.display = "block";
    setPlaceholder();
};


function resetGame() {
    "use strict";
    // resets game state
    // reset a number of guessed albums
    guessedCount = 0;
    const successIconList = document.querySelectorAll('.success-icon');
    // remove 'check mark' icons
    successIconList.forEach(icon => icon.classList.remove('visible'));
    // remove a description of the album
    const coverArtList = document.querySelectorAll('.cover-art');
    coverArtList.forEach(image => image.alt="");
};



function loadFailureArt(node, failData) {
    "use strict";
    frequentElements.gameFrame.classList.add("shadow-main");
    const failureArt = document.createElement("img");
    const failureArtURL = failData['failure_art'];
    failureArt.src = failureArtURL;
    failureArt.classList.add("failure-art");

    const failureArtBlock = document.createElement("div");
    failureArtBlock.classList.add("failure-art-block", "shadow-main");

    const failureArtText = document.createElement("h1");
    failureArtText.classList.add("text-light")
    failureArtText.textContent = "someone made an oopsie!"

    failureArtBlock.appendChild(failureArtText);

    node.appendChild(failureArt);
    node.appendChild(failureArtBlock);
};


function loadSpinner(node) {
    "use strict";
    const spinner = document.createElement("img");
    const url = "static/images/loading/spinner-vinyl-64.gif";
    spinner.classList.add('spinner');
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
    tooltip.textContent = el.dataset.tooltip;
    el.appendChild(tooltip);
});