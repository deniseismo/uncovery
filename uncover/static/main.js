import {AlbumGameInfo} from "./game.js"
import {frequentElements, insertAfter, addTooltips} from './utils.js'
import {winningMessage} from './info.js'
import {MusicFilter} from './musicFilter.js'
import {prepareToExplore, cleanAfterExplore} from './explore.js'
import {animateCoverArt, animateWaves} from './animation.js'
import anime from './anime.es.js';


const albumGame = new AlbumGameInfo();

export const musicFilters = new MusicFilter({
  tags: ['hip-hop', 'jazz'],
  timeSpan: [1967, 2015]
})



export const submitInput = function() {
  // make 'play-button' disappear
  frequentElements.playButton.classList.remove("visible");
  // make 'download-button' disappear
  frequentElements.downloadButton.classList.remove("visible");
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
  let qualifier = '';
  let option = frequentElements.selectOptions.value
  if (desiredMethod === "explore") {
    const timeSpanSlider = document.getElementById('time-span-slider');

    option = {
      "genres": musicFilters.tagsPickedInfo,
      "time_span": timeSpanSlider.noUiSlider.get()
    }
  } else {
    qualifier = document.querySelector('#text-field').value;
  };
  fetch(`${desiredMethod}`, {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json'
    }),
    body: JSON.stringify({
      "qualifier": qualifier,
      "option": option
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
    albumGame.albums = data['albums'];
    console.log(albumGame);
    // restores a 'valid' form style
    frequentElements.textField.classList.remove("is-invalid");
    // when done, removes current pictures from the frame, adds new ones
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
    const referenceNode = document.querySelector(".search-and-options-container");
    insertAfter(progressBar, referenceNode);
//    const waves = document.querySelectorAll('.wave');
//    waves.forEach(wave => wave.classList.add('falldown'));
    /* waiting for all images to load before showing them up*/
    $('#game-frame').waitForImages(function() {
      /* remove progress bar once loaded */
      progressBar.remove();
      /* remove 'loading' class that blocks animation of albums images */
      this.classList.remove("loading");
      const itemsList = document.querySelectorAll(".flex-item");
      itemsList.forEach(item => {
        item.classList.add("loaded");
      });

      frequentElements.playButton.classList.add("visible");
      frequentElements.downloadButton.classList.add("visible");
      animateCoverArt();
      animateWaves(desiredMethod);
      const waves = document.querySelectorAll('.wave');
      waves.forEach(wave => wave.classList.remove('falldown'));

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
submitForm.addEventListener('submit', () => {
  // checks if the game is not on
  if (submitForm.id === 'submit-form') {
    submitInput();
  }
});


frequentElements.downloadButton.addEventListener('click', () => {
  frequentElements.downloadButton.value = "WAIT FOR IT…";
  fetch("save_collage", {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json'
    }),
    body: JSON.stringify({
      "images": albumGame.albums.map(album => album.image)
    })
  }).then(response => response.json()).then(data => {
    const myLink = document.createElement('a');
    myLink.href = data;
    myLink.target = "_blank";
    document.body.appendChild(myLink);
    myLink.click();
    frequentElements.downloadButton.value = "SAVE COLLAGE";
  });
});

// play button
frequentElements.playButton.onclick = (e) => {
  // reset score, remove 'success' icons
  resetGame();
  e.target.classList.toggle('on');
  e.target.classList.remove('won');
  if (e.target.classList.contains('on')) {
    prepareGame();
    const input = document.querySelector('#play-field');
    input.oninput = handleGuesses;
  } else {
    cancelGame();
  };
};


function handleGuesses(e) {
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
  const fuse = new Fuse(albumGame.notGuessedAlbums, options);
  const pattern = e.target.value;
  const results = fuse.search(pattern).length;
  if (results > 0) {
    const albumID = fuse.search(pattern)[0]['item']['id'];
    console.log(`search results: ${fuse.search(pattern)[0]['item']['title']}`);
    highlightGuessedAlbum(albumID);
    updateScore();
    albumGame.removeGuessedAlbum(albumID);
    frequentElements.textField.value ='';
  }
};


// highlights the guessed album with animation & puts the success icon over the image
function highlightGuessedAlbum(albumID) {
  const guessedAlbum = document.querySelector(`.art-${albumID}`);
  const title = albumGame.albums[albumID]['title'];

  guessedAlbum.classList.remove("guessed-right");
  /**
   trigger a reflow in between removing and adding the class name © css-tricks.com
   helps restarting animation & playing it again if needed
  */
  void guessedAlbum.offsetWidth;
  guessedAlbum.classList.add("guessed-right");
  guessedAlbum.alt = title;
  const successIcon = document.querySelector(`#success-${albumID}`);
  successIcon.classList.add('visible');
};

// updates score
function updateScore() {
  const totalAmountOfAlbums = albumGame.albums.length;
  const total = Math.min(totalAmountOfAlbums, 9);
  albumGame.incrementAlbumsCount();
  const scoreText = document.querySelector(".score-text");
  if (albumGame.albumsCount === total) {
    // triggers winning function if all albums guessed
    gameWon();
  } else {
    // updates the message otherwise
    scoreText.textContent = `Wowee! You've guessed ${albumGame.albumsCount} out of ${total}.`;
  }
};

// handles winning
function gameWon() {
  const scoreText = document.querySelector(".score-text");
  const randomIndex = Math.floor(Math.random() * winningMessage.length);
  scoreText.textContent = winningMessage[randomIndex]["quote"];
  const scoreContainer = document.querySelector('.score-container');
  scoreContainer.classList.add('info-tooltip', 'score-game-won');
  scoreContainer.setAttribute("data-tooltip", winningMessage[randomIndex]["credits"]);
  addTooltips();
  frequentElements.playButton.value = 'PLAY SOME MORE';
  frequentElements.playButton.classList.add('won');
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
  const targetButtonID = event.target.id;
  console.log(`event target: ${targetButtonID}`);
  console.log(frequentElements.activeButtonID());
  configureOptionsStyle(targetButtonID);
  const methodButtonsList = document.querySelectorAll(".method");
  methodButtonsList.forEach(button => button.classList.remove('active'));
  event.target.classList.add('active');
  const sliderContainer = document.querySelector('.slider-container');
  const musicGenresContainer = document.querySelector('.music-genres-container');
  if (!(event.target.id === "explore")) {
    if (sliderContainer) {
      sliderContainer.remove();
      musicGenresContainer.remove();
    };
    const tagsForm = document.querySelector('#tags-form');
    if (tagsForm) {
      tagsForm.id = 'submit-form';
    }
  };
});

/* displays 'options' menu when the input's focused  */
let timerID;
[frequentElements.textField, frequentElements.selectOptions].forEach(item => {
  item.addEventListener('focusin', () => {
    clearTimeout(timerID);
    // make sure the button's 'username' and the game is off
    if (frequentElements.activeButtonID() === 'by_username' && !(frequentElements.playButton.classList.contains('on'))) {
      frequentElements.selectOptions.style.display = 'block';
    };
  });
});

[frequentElements.textField, frequentElements.selectOptions].forEach(item => {
  item.addEventListener('focusout', () => {
    timerID = setTimeout(function() {
      $(".select-options").hide();
  }, 10);
  });
});

// fixes artist's name as per last.fm correction
function fixArtistName(data) {
  if (frequentElements.activeButtonID() === 'by_artist') {
    frequentElements.textField.value = data['info'];
  };
};

// loads cover art images to the main game frame
function loadCoverArt(data) {
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
  resizeCoverArtImages(length);
};

function resizeCoverArtImages(amountOfAlbums) {
  console.log(amountOfAlbums);
  switch (amountOfAlbums) {
    case 1:
      const albumImage = document.querySelector(".cover-art");
      albumImage.classList.add('cover-big');
      break;
    case 2:
    case 4:
      const albumImagesList = document.querySelectorAll(".cover-art");
      albumImagesList.forEach((image) => image.classList.add('cover-medium'));
      break;
    case 5:
    case 8:
      console.log(document.querySelector('.art-0'), document.querySelector('.art-1'));
      [document.querySelector(".art-0"), document.querySelector(".art-1")]
        .forEach((image) => image.classList.add('cover-medium'));
      break;
    case 7:
      [document.querySelector(".art-0"), document.querySelector(".art-1"),
      document.querySelector(".art-2")]
        .forEach((image) => image.classList.add('cover-medium'));

      [document.querySelector(".art-3"), document.querySelector(".art-4"),
      document.querySelector(".art-5"), document.querySelector(".art-6")]
        .forEach((image) => image.classList.add('cover-small'));
      const referenceNode = document.querySelector('#item-2');
      const specialContainer = document.createElement('div');
      specialContainer.classList.add('seven-albums-special-container');
      insertAfter(specialContainer, referenceNode);
      [document.querySelector("#item-3"), document.querySelector("#item-4"),
        document.querySelector("#item-5"), document.querySelector("#item-6")]
        .forEach((item) => specialContainer.appendChild(item));
      break;
  }
};


function setPlaceholder(targetButtonID) {
  const options = {
    "by_username": "last.fm username",
    "by_artist": "artist name",
    "by_spotify": "Spotify Playlist Link",
    "explore": "music tags/genres"
  }
  frequentElements.textField.placeholder = options[targetButtonID];
};



function prepareGame() {
  hideOptions('on');
  createScoreContainer();
  frequentElements.textField.id = 'play-field';
  frequentElements.textField.placeholder = 'Can you name all the albums?';
  frequentElements.textField.value = '';
  frequentElements.textField.focus();
  const formContainer = document.querySelector(".form-container");
  formContainer.id = "guess-form";
  frequentElements.playButton.value = 'GIVE UP';
  const okButton = document.querySelector(".ok-btn");
  okButton.style.display = "none";
  albumGame.notGuessedAlbums = [...albumGame.albums];
};

function createScoreContainer() {
  const scoreContainer = document.createElement("div");
  scoreContainer.classList.add("flex-container", "shadow-main", "score-container");
  const scoreText = document.createElement("h1");
  scoreText.classList.add("score-text");
  scoreText.textContent = "You haven't guessed any albums yet. 😟";
  scoreContainer.appendChild(scoreText);
  const referenceNode = document.querySelector(".search-and-options-container");
  insertAfter(scoreContainer, referenceNode);
}


function cancelGame() {

  const scoreContainer = document.querySelector('.score-container');
  if (scoreContainer) {
    scoreContainer.remove();
  };
  const formContainer = document.querySelector(".form-container");
  let defaultForm = 'submit-form';
  if (frequentElements.activeButtonID() === 'explore') {
    defaultForm = 'tags-form';
    const sliderContainer = document.querySelector('.slider-container');
    if (sliderContainer) {
      sliderContainer.style.display = 'flex';
    };
  };
  formContainer.id = defaultForm;
  console.log(formContainer.id);
  frequentElements.playButton.value = 'GUESS ALBUMS';
  if (frequentElements.playButton.classList.contains('on')) {
    frequentElements.playButton.classList.remove('on');
  };
  const okButton = document.querySelector(".ok-btn");
  okButton.style.display = "block";
  setPlaceholder(frequentElements.activeButtonID());
};

function resetGame() {
  // resets game state
  // reset a number of guessed albums
  albumGame.albumsCount = 0;
  const successIconList = document.querySelectorAll('.success-icon');
  // remove 'check mark' icons
  successIconList.forEach(icon => icon.classList.remove('visible'));
  // remove a description of the album
  const coverArtList = document.querySelectorAll('.cover-art');
  coverArtList.forEach(image => {
    image.alt = "";
  });
};

function loadFailureArt(node, failData) {
  frequentElements.gameFrame.classList.add("shadow-main");
  const failureArt = document.createElement("img");
  const failureArtURL = failData['failure_art'];
  failureArt.src = failureArtURL;
  failureArt.classList.add("failure-art");

  const failureArtBlock = document.createElement("div");
  failureArtBlock.classList.add("failure-art-block", "shadow-main");

  const failureArtText = document.createElement("h1");
  failureArtText.classList.add("text-light");
  failureArtText.textContent = "someone made an oopsie!";

  failureArtBlock.appendChild(failureArtText);

  node.appendChild(failureArt);
  node.appendChild(failureArtBlock);
};

function loadSpinner(node) {
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
const tooltipElements = document.querySelectorAll('.info-tooltip');
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






function hideOptions() {
  frequentElements.selectOptions.style.display = 'none';

  const sliderContainer = document.querySelector('.slider-container');
  if (sliderContainer) {
    sliderContainer.style.display = 'none';
  };

  const scoreContainer = document.querySelector('.score-container');
  if (scoreContainer) {
    scoreContainer.style.display = "none";
  };
};

function configureOptionsStyle(targetButtonID) {
  // if a button pressed is a new button/new destination
  if (targetButtonID !== frequentElements.activeButtonID()) {
    // change the placeholder to the correct one
    // cancel the game
    cancelGame();
    if (targetButtonID === "explore") {
      prepareToExplore();
    } else if (frequentElements.activeButtonID() === "explore") {
      cleanAfterExplore();
    }
    setPlaceholder(targetButtonID);
    frequentElements.textField.value = '';
  }
};


