import {frequentElements, addTooltips} from './utils.js'
import {theGame, albumGame} from './main.js'
import {setPlaceholder} from './uiconfig.js'
import {handleTags} from './explore.js'
import {hideOptions} from './uiconfig.js'
import {insertAfter} from './utils.js'
import {winningMessage} from './info.js'
import anime from './anime.es.js'


export class Game {
  constructor(status) {
    this.isOn = status;
  }
  get status() {
    return this.isOn;
  }
  set status(status) {
    this.isOn = status;
  }
}


export class AlbumGameInfo {
  constructor() {
    this.albumsList = [];
    this.notGuessedAlbumsList = [];
    this.guessedAlbumsCount = 0;
  };
  set albums(albums) {
    this.albumsList = albums;
  };
  get albums() {
    return this.albumsList;
  };
  set notGuessedAlbums(albums) {
    this.notGuessedAlbumsList = albums;
  };
  get notGuessedAlbums() {
    return this.notGuessedAlbumsList;
  };
  incrementAlbumsCount() {
    this.guessedAlbumsCount++;
  };
  get albumsCount() {
    return this.guessedAlbumsCount;
  }
  set albumsCount(newCount) {
    this.guessedAlbumsCount = newCount;
  }
  removeGuessedAlbum(guessedAlbumID) {
    console.log(this);

    for (let i = 0; i < this.notGuessedAlbumsList.length; i++) {
      if (this.notGuessedAlbumsList[i]['id'] === guessedAlbumID) {
        console.log(this.notGuessedAlbumsList);
        this.notGuessedAlbumsList.splice(i, 1);
        return true;
      };
    };
  };
};


export function handleGuesses(e) {
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
//  guessedAlbum.classList.add("guessed-right");
  anime({
    targets: guessedAlbum,
    opacity: [
      {value: 0.3, easing: 'easeOutElastic(5, 0.3)', duration: 200},
      {value: 1, easing: 'easeOutElastic(5, 0.3)', duration: 400}
    ]
  });
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

export function prepareGame() {
  theGame.status = true;
  hideOptions('on');
  createScoreContainer();
  const formField = document.querySelector('.form-field');
  formField.removeEventListener("input", handleTags);
  $('.form-field').autocomplete('disable');
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


export function cancelGame() {
  theGame.status = false;
  const scoreContainer = document.querySelector('.score-container');
  if (scoreContainer) {
    scoreContainer.remove();
  };
  const formContainer = document.querySelector(".form-container");
  let defaultForm = 'submit-form';
  if (frequentElements.activeButtonID() === 'explore') {
    console.log('canceled but explore')
    const formField = document.querySelector('.form-field');
    formField.addEventListener("input", handleTags);
    $('.form-field').autocomplete('enable');
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
  resetGame();
};

export function resetGame() {
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