// main global object with all the info about albums & album covers
let albums;
let notGuessedAlbums;
// a global variable that stores a number of albums guessed so far
let guessedCount = 0;
/* main AJAX function */
let timeSpan;
let tagsPicked = [];
let currentMusicGenre = '';

const frequentElements = {
  gameFrame: document.querySelector('#game-frame'),
  playButton: document.querySelector('#play-button'),
  downloadButton: document.querySelector('#download-button'),
  textField: document.querySelector('#text-field'),
  selectOptions: document.querySelector('.select-options'),
  searchAndOptionsContainer: document.querySelector('.search-and-options-container'),
  activeButtonID() { return document.querySelector('.button.active').id }
};

const submitInput = function() {
  "use strict";
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
      "genres": tagsPicked,
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
    albums = data['albums'];
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
    const waves = document.querySelectorAll('.wave');
    waves.forEach(wave => wave.classList.add('falldown'));
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
//      const collageURL = document.querySelector('#collage-link');
//      collageURL.href = data['collage'];

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
submitForm.addEventListener('submit', () => {
  // checks if the game is not on
  if (submitForm.id === 'submit-form') {
    submitInput();
  }
});


frequentElements.downloadButton.addEventListener('click', () => {
  "use strict";
  frequentElements.downloadButton.value = "WAIT FOR IT…";
  fetch("save_collage", {
    method: 'POST',
    headers: new Headers({
      'Content-Type': 'application/json'
    }),
    body: JSON.stringify({
      "images": albums.map(album => album.image)
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
  "use strict";
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
  const results = fuse.search(pattern).length;
  if (results > 0) {
    const albumID = fuse.search(pattern)[0]['item']['id'];
    console.log(`search results: ${fuse.search(pattern)[0]['item']['title']}`);
    highlightGuessedAlbum(albumID);
    updateScore();
    removeGuessedAlbum(albumID);
    frequentElements.textField.value ='';
  }
};


// highlights the guessed album with animation & puts the success icon over the image
function highlightGuessedAlbum(albumID) {
  const guessedAlbum = document.querySelector(`.art-${albumID}`);
  const title = albums[albumID]['title'];

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
  const totalAmountOfAlbums = albums.length;
  const total = Math.min(totalAmountOfAlbums, 9);
  guessedCount++;
  const scoreText = document.querySelector(".score-text");
  if (guessedCount === total) {
    // triggers winning function if all albums guessed
    gameWon();
  } else {
    // updates the message otherwise
    scoreText.textContent = `Wowee! You've guessed ${guessedCount} out of ${total}.`;
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

// an array of winning messages (song lyrics, etc.)
const winningMessage = [
  {
    'quote': "I wanna be adored!",
    'credits': "© The Stone Roses — I Wanna be Adored"
  },
  {
    'quote': "I'm worth a million in prizes!",
    'credits': "© Iggy Pop — Lust for Life"
  },
  {
    'quote': "You are invited by anyone to do anything!",
    'credits': "© Dismemberment Plan — You are Invited"
  },
  {
    'quote': "I'm on a roll this time",
    'credits': "© Radiohead — Lucky"
  },
  {
    'quote': "And you may ask yourself, well, how did I get here?",
    'credits': "© Talking Heads — Once in a Lifetime"
  },
  {
    'quote': "I'm a genius, a prodigy, a demon at Maths & Science, I'm up for a prize!",
    'credits': "© Belle and Sebastian — Act of the Apostle II"
  },
  {
    'quote': "I've never been wrong",
    'credits': "© LCD Soundsystem — Losing My Edge"
  },
  {
    'quote': "Get a drink, have a good time now. Welcome to paradise, paradise, paradise",
    'credits': "The Avalanches — Since I Left you"
  }
];



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

function insertAfter(newNode, referenceNode) {
    referenceNode.parentNode.insertBefore(newNode, referenceNode.nextSibling);
};


// removes an album from the list of guessed albums so that it didn't count more than once
function removeGuessedAlbum(albumID) {
  "use strict";
  for (let i = 0; i < notGuessedAlbums.length; i++) {
    if (notGuessedAlbums[i]['id'] === albumID) {
      notGuessedAlbums.splice(i, 1);
      return true;
    }
  }
};

function setPlaceholder() {
  "use strict";
  if (frequentElements.activeButtonID() === 'by_username') {
    frequentElements.textField.placeholder = 'last.fm username';
  } else if (frequentElements.activeButtonID() === 'by_artist') {
    frequentElements.textField.placeholder = 'artist name';
  } else if (frequentElements.activeButtonID() === 'explore'){
    frequentElements.textField.placeholder = 'music tags/genres';
  };
}

function prepareGame() {
  "use strict";
  const scoreContainer = document.querySelector('.score-container');
  frequentElements.textField.id = 'play-field';
  frequentElements.textField.placeholder = 'Can you name all the albums?';
  frequentElements.textField.value = '';
  frequentElements.textField.focus();
  const submitForm = document.querySelector("#submit-form");
  if (submitForm) {
    submitForm.id = 'guess-form';
  } else {
  const tagsForm = document.querySelector("#tags-form");
    if (tagsForm) {
      tagsForm.id = 'tags-form';
    }
  };
  frequentElements.selectOptions.style.display = 'none';
  const sliderContainer = document.querySelector('.slider-container');
  if (sliderContainer) {
    sliderContainer.style.display = 'none';
  };
  scoreContainer.style.display = "block";
  const scoreText = document.querySelector(".score-text");
  scoreText.textContent = "You haven't guessed any albums yet. 😟"
  frequentElements.playButton.value = 'GIVE UP';
  const okButton = document.querySelector(".ok-btn");
  okButton.style.display = "none";
  notGuessedAlbums = albums.slice(0, 10);
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
  let defaultForm = 'submit-form';
  if (frequentElements.activeButtonID() === 'explore') {
    defaultForm = 'tags-form';
    const sliderContainer = document.querySelector('.slider-container');
    if (sliderContainer) {
      sliderContainer.style.display = 'flex';
    };
  };
  guessForm.id = defaultForm;
  const methodButtonsList = document.querySelectorAll(".method");
  methodButtonsList.forEach(button => button.style.display = 'block');
  frequentElements.playButton.value = 'GUESS ALBUMS';
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
  coverArtList.forEach(image => {
    image.alt = "";
  });
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
  failureArtText.classList.add("text-light");
  failureArtText.textContent = "someone made an oopsie!";

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

function addTooltips() {
  const tooltippedElements = document.querySelectorAll('.info-tooltip')
  tooltippedElements.forEach((element) => {
    const tooltip = document.createElement('label');
    tooltip.classList.add('tooltipText');
    tooltip.textContent = element.dataset.tooltip;
    element.appendChild(tooltip);
  });
};


const exploreButton = document.querySelector("#explore");
exploreButton.addEventListener("click", (event) => {

  if (!(frequentElements.activeButtonID() === 'explore')) {
    createSliderContainer();
    createSlider();
    createMusicGenresContainer();
    frequentElements.textField.id = "tag-field";
    const submitForm = document.querySelector("#submit-form");
    submitForm.id = 'tags-form';
  }
  const tagsSearchInput = document.querySelector('#tag-field');
  tagsSearchInput.oninput = handleTags;
})


function createSliderContainer() {
  const okButton = document.querySelector(".ok-btn");
  okButton.value = 'ADD';
  okButton.disabled = true;
  okButton.addEventListener('click', addMusicTags);
  const sliderContainer = document.createElement("div");
  sliderContainer.classList.add('slider-container');
  const sliderBar = document.createElement("div");
  sliderBar.classList.add('slider-bar');
  const sliderLabel = document.createElement("div");
  sliderLabel.classList.add('slider-label');
  sliderLabel.textContent = "The Times They Are A-Changin'"
  const slider = document.createElement("div");
  slider.id = "time-span-slider";
  sliderBar.appendChild(sliderLabel);
  sliderBar.appendChild(slider);
  const filterButton = document.createElement('input');
  filterButton.id = 'submit-filter';
  filterButton.type = 'submit';
  filterButton.value = 'uncover';
  filterButton.classList.add('btn', 'button', 'shadow-main', 'play-button', 'visible');
  filterButton.addEventListener('click', submitInput);
  sliderContainer.appendChild(sliderBar);
  sliderContainer.appendChild(filterButton);
  frequentElements.searchAndOptionsContainer.appendChild(sliderContainer);
}

function addMusicTags() {
  if (frequentElements.activeButtonID() === 'explore') {
    const tagsSearchInput = document.querySelector('#tag-field');
    if (tagsPicked.length > 2) {
      console.log('too many tags to filter');
      return false;
    };
    if (!(tagsPicked.includes(currentMusicGenre))) {
      tagsPicked.push(currentMusicGenre);
      createMusicGenreElement(currentMusicGenre);
      console.log(`${currentMusicGenre} was successfully added to the tags.`);
      console.log(tagsPicked);
    } else {
      console.log(`${currentMusicGenre} already exists.`);
      return false;
    };
  }
};

function createMusicGenresContainer() {
  const musicGenresContainer = document.createElement('div');
  musicGenresContainer.classList.add('music-genres-container', 'shadow-main');
  const selectedFilters = document.createElement('h1');
  selectedFilters.textContent = "FILTERS SELECTED";
  const timeSpanElement = document.createElement('p');
  timeSpanElement.classList.add('time-span');
  const timeSpanSlider = document.querySelector('#time-span-slider');
  const timeSpan = timeSpanSlider.noUiSlider.get();
  timeSpanElement.textContent = `${timeSpan[0]}—${timeSpan[1]}`;
  musicGenresContainer.appendChild(selectedFilters);
  musicGenresContainer.appendChild(timeSpanElement);
  document.querySelector('main').appendChild(musicGenresContainer);
};


function createMusicGenreElement(musicGenre) {
  const musicGenreElement = document.createElement('p');
  musicGenreElement.classList.add('music-genre-element', 'shadow-main');
  musicGenreElement.id = musicGenre;
  musicGenreElement.textContent = `${musicGenre}`;
  const musicGenresContainer = document.querySelector('.music-genres-container');
  musicGenresContainer.appendChild(musicGenreElement);
  document.querySelectorAll('.music-genre-element').forEach(genre => {
    genre.addEventListener('click', (e) => {
          for (let i = 0; i < tagsPicked.length; i++) {
        if (tagsPicked[i] === e.target.id) {
          tagsPicked.splice(i, 1);
        };
      };
      e.target.remove();
    });

  });
};


function createSlider() {
    const timeSpanSlider = document.getElementById('time-span-slider');

    noUiSlider.create(timeSpanSlider, {
        start: [1967, 2015],
        tooltips: true,
        connect: true,
        padding: 0,
        step: 1,
        range: {
            'min': 1950,
            'max': 2020
        },
        pips: {
            mode: 'values',
            values: [1965, 1985, 2010],
            density: 10
        },
        format: {
            to: function (value) {
                return parseInt(value);
            },
            from: function (value) {
                return parseInt(value);
            }
        }
    });

    timeSpanSlider.noUiSlider.on('change', (values, handle) => {
        timeSpan = timeSpanSlider.noUiSlider.get();
        const timeSpanElement = document.querySelector('.time-span');
        timeSpanElement.textContent = `${timeSpan[0]}–${timeSpan[1]}`;
    });
};


async function handleTags(e) {
  "use strict";
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
  const tags_list = await fetchTags();
  const fuse = new Fuse(tags_list, options);
  const pattern = e.target.value;
  const results = fuse.search(pattern).length;
  if (results > 0) {
    console.log(fuse.search(pattern));
    const okButton = document.querySelector(".ok-btn");
    currentMusicGenre = fuse.search(pattern)[0]['item'];
    okButton.disabled = false;
  } else {
    const okButton = document.querySelector(".ok-btn");
    okButton.disabled = true;
  };
};


async function fetchTags() {
  const response = await fetch('get_tags');
  const tags = await response.json();
  return tags;
}

