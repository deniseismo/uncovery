import {AlbumGameInfo, Game, playInit} from "./game.js"
import {MusicFilter} from './musicFilter.js'
import {addTooltips, frequentElements, insertAfter, removeAllChildNodes, loadSpinner} from './utils.js'
import {configureOptionsStyle, removePlayButtons, createPlayButtons, resetPlayButtons} from './uiconfig.js'
import {animateCoverArt, animateWaves, animatePlayButtons} from './animation.js'

export const theGame = new Game(false);

export const albumGame = new AlbumGameInfo();

export const musicFilters = new MusicFilter({
  tags: ['hip-hop', 'jazz'],
  timeSpan: [1967, 2015]
})



export const submitInput = function() {
  removePlayButtons();
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

    option = {
      "genres": musicFilters.tagsPickedInfo,
      "time_span": musicFilters.timeSpanInfo
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
      animateCoverArt();
      createPlayButtons(desiredMethod);
      const total = Math.min(albumGame.albums.length, 9);
      animatePlayButtons('.play-buttons-container .play-button', total);
      animateWaves(desiredMethod);
      const waves = document.querySelectorAll('.wave');
      waves.forEach(wave => wave.classList.remove('falldown'));
      downloadInit();
      playInit();

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

function downloadInit() {
  const downloadButton = document.querySelector('#download-button');
  downloadButton.addEventListener('click', () => {
  downloadButton.value = "WAIT FOR IT…";
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
    downloadButton.value = "SAVE COLLAGE";
  });
});
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
    if (frequentElements.activeButtonID() === 'by_username' && !(theGame.status)) {
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
  let length = Math.min(totalAmountOfAlbums, 9);
  for (let i = 0; i < length; i++) {
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

// initialize/create the tooltips
addTooltips();