import {frequentElements, addTooltips, insertAfter} from './utils.js'
import {theGame, albumGame} from './main.js'
import {setPlaceholder} from './uiconfig.js'
import {handleTags} from './explore.js'
import {hideOptions, resetPlayButtons} from './uiconfig.js'
import {winningMessage} from './info.js'
import {animateHighlightGuessedAlbum, animateWinningMessage} from './animation.js'
import {hideUncoverModeForGame, backToRealityFromTheGame} from './albuminfobox.js'


export class Game {
  constructor(status) {
    this.isOn = status;
    this.mode = '';
    this.uncovery = false;
  }
  get status() {
    return this.isOn;
  }
  set status(status) {
    this.isOn = status;
  }
  get playMode() {
    return this.mode;
  }
  set playMode(theMode) {
    this.mode = theMode;
  }
  set uncoveryStatus(mode) {
    this.uncovery = mode;
  }
  get uncoveryStatus() {
    return this.uncovery;
  }
}

// a list of current albums
export class AlbumGameInfo {
  constructor() {
    this.albumsList = [];
    this.notGuessedAlbumsList = [];
    this.guessedAlbumsCount = 0;
    this.query = '';
    this.type = '';
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
  get currentQuery() {
    return this.query;
  }
  set currentQuery(value) {
    this.query = value;
  }
  get currentType() {
    return this.type;
  }
  set currentType(value) {
    this.type = value;
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

// initialize all the necessary event listeners for play buttons
export function playInit() {
// play button
  const playButtons = document.querySelectorAll('.play-buttons-container .guess');
  playButtons.forEach(button => {
    button.addEventListener("click", (e) => {
      resetGame();
      resetPlayButtons(e.target.id);
      e.target.classList.toggle('on');
      e.target.classList.remove('won');
      if (e.target.classList.contains('on')) {
        prepareGame(e.target);
      } else {
        console.log('cancel');
        cancelGame(e.target);
        const formField = document.querySelector('.form-field');
        formField.value = albumGame.currentQuery;
      };
    })
  })
}

// handles album/artist guesses (depends on the game mode)
function handleGuesses(e) {
  let searchMode = "names";
  if (theGame.playMode === 'artists') {
    searchMode = "artist_names";
  }
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
      searchMode, // albums/artists
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
  animateHighlightGuessedAlbum(guessedAlbum);
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
  // updates the message
  scoreText.textContent = `Wowee! You've guessed ${albumGame.albumsCount} out of ${total}.`;
  if (albumGame.albumsCount === total) {
    // triggers winning function if all albums guessed
    gameWon();
  }
};

// handles winning
function gameWon() {
  const currentButton = document.querySelector('.play-button.on');
  currentButton.value = 'PLAY SOME MORE';
  currentButton.classList.add('won');
  createWinningContainer();
  animateWinningMessage();
  addTooltips();
};

function createWinningContainer() {
  const winningContainer = document.createElement('div');
  winningContainer.id = 'winning-container';
  winningContainer.classList.add('winning-container', 'info-tooltip');
  const winningText = document.createElement('p');
  winningText.classList.add('winning-text');
  const randomIndex = Math.floor(Math.random() * winningMessage.length);
  winningText.textContent = winningMessage[randomIndex]["quote"];
  winningContainer.appendChild(winningText);
  winningContainer.setAttribute("data-tooltip", winningMessage[randomIndex]["credits"]);
  //frequentElements.gameFrame.appendChild(winningContainer);
  document.querySelector('.wrapper').appendChild(winningContainer);
  winningContainer.addEventListener('click', (e) => {
    setTimeout(() => {
        e.target.remove();
      }, 100);
  });
}

// handles game preparation
function prepareGame(buttonPressed) {
  const formField = document.querySelector('.form-field');
  theGame.status = true;
  let mode = 'albums';
  if (buttonPressed.id == 'guess-artists') {
    mode = 'artists';
  }
  hideUncoverModeForGame();
  theGame.playMode = mode;
  hideOptions('on');
  createScoreContainer();
  formField.removeEventListener("input", handleTags);
  $('.form-field').autocomplete('disable');
  const inputField = document.querySelector('.text-field-container');
  inputField.style.display = 'flex';
  frequentElements.textField.id = 'play-field';
  frequentElements.textField.placeholder = `Can you name all the ${mode}?`;
  frequentElements.textField.value = '';
  frequentElements.textField.focus();
  const formContainer = document.querySelector(".form-container");
  formContainer.id = "guess-form";
  buttonPressed.value = 'GIVE UP';
  const okButton = document.querySelector(".ok-btn");
  okButton.style.display = "none";
  albumGame.notGuessedAlbums = [...albumGame.albums];
  const input = document.querySelector('#play-field');
  input.oninput = handleGuesses;
};

// creates a score container
function createScoreContainer() {
  const scoreContainer = document.createElement("div");
  scoreContainer.classList.add("flex-container", "shadow-main", "score-container");
  const scoreText = document.createElement("h1");
  scoreText.classList.add("score-text");
  scoreText.textContent = `You haven't guessed any ${theGame.playMode} yet. 😟`;
  scoreContainer.appendChild(scoreText);
  const referenceNode = document.querySelector(".search-and-options-container");
  insertAfter(scoreContainer, referenceNode);
}


// cancels the game
export function cancelGame(buttonPressed) {
  theGame.status = false;
  const scoreContainer = document.querySelector('.score-container');
  if (scoreContainer) {
    scoreContainer.remove();
  };
  const formContainer = document.querySelector(".form-container");
  let defaultForm = 'submit-form';
  if (frequentElements.activeButtonID() === 'explore') {
    defaultForm = 'tags-form';
  } else {
    const formField = document.querySelector('.form-field');
    formField.id = 'text-field';
  };
  if (frequentElements.activeButtonID() === 'by_spotify') {
    const inputField = document.querySelector('.text-field-container');
    inputField.style.display = 'none';
  }
  formContainer.id = defaultForm;

  buttonPressed.value = 'GUESS ALBUMS';
  if (buttonPressed.classList.contains('on')) {
    buttonPressed.classList.remove('on');
    buttonPressed.classList.remove('won');
  };
  const okButton = document.querySelector(".ok-btn");
  okButton.style.display = "block";
  setPlaceholder(frequentElements.activeButtonID());
  resetGame();
  backToRealityFromTheGame();
};

// resets the game
function resetGame() {
  // resets game state
  // reset a number of guessed albums
  const input = document.querySelector('.form-field');
  input.removeEventListener('oninput', handleGuesses);
  albumGame.albumsCount = 0;
  const successIconList = document.querySelectorAll('.success-icon');
  // remove 'check mark' icons
  successIconList.forEach(icon => icon.classList.remove('visible'));
  // remove a description of the album
  const coverArtList = document.querySelectorAll('.cover-art');
  coverArtList.forEach(image => {
    image.alt = "album cover art";
  });
};