import {frequentElements, removeAllChildNodes, insertAfter} from './utils.js'
import {cancelGame} from './game.js'
import {prepareToExplore, cleanAfterExplore} from './explore.js'
import {renderAboutPage} from './about.js';
import {theGame} from "./main.js";

export function hideOptions() {
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

export function configureOptionsStyle(targetButtonID) {
  // if a button pressed is a new button/new destination
  if (targetButtonID !== frequentElements.activeButtonID()) {
    // change the placeholder to the correct one
    // cancel the game
    if (theGame.status) {
      cancelGame();
    }
    if (targetButtonID === "explore") {
      prepareToExplore();
    } else if (frequentElements.activeButtonID() === "explore") {
      cleanAfterExplore();
    }
    if (targetButtonID === "about") {
      renderAboutPage();
    } else if (frequentElements.activeButtonID() === "about") {
      const searchBar = document.querySelector(".search-and-options-container");
      searchBar.style.display = 'block';
      removeAllChildNodes(frequentElements.gameFrame);
    }

    setPlaceholder(targetButtonID);
    frequentElements.textField.value = '';
  }
};

export function setPlaceholder(targetButtonID) {
  const options = {
    "by_username": "last.fm username",
    "by_artist": "artist name",
    "by_spotify": "Spotify Playlist Link",
    "explore": "music tags/genres"
  }
  frequentElements.textField.placeholder = options[targetButtonID];
};

export function createPlayButtons(method) {
  const flexContainer = document.createElement('div');
  flexContainer.classList.add('flex-container', 'play-buttons-container');
  // button generator
  function createButton(value, id) {
    const someButton = document.createElement('input');
    someButton.classList.add("button", "btn", "shadow-main", "play-button", "visible", "guess");
    someButton.type = "button";
    someButton.id = id;
    someButton.value = value;
    return someButton;
  };

  const downloadButton = createButton('SAVE COLLAGE', 'download-button');
  downloadButton.classList.remove('guess');
  const guessAlbums = createButton('GUESS ALBUMS', 'guess-albums');
  flexContainer.appendChild(guessAlbums);
  flexContainer.appendChild(downloadButton);
  if (!(method === 'by_artist')) {
    const guessArtists = createButton('GUESS ARTISTS', 'guess-artists');
    // inserts 'guess artists' button after 'guess albums' button
    insertAfter(guessArtists, guessAlbums);
  };
  // inserts a container with all the buttons after the Game Frame
  insertAfter(flexContainer, frequentElements.gameFrame);
};

export function removePlayButtons() {
  const buttonsContainer = document.querySelector('.play-buttons-container');
  if (buttonsContainer){
    buttonsContainer.remove();
  }
};


export function resetPlayButtons(pressedButtonID) {
  const playButtons = document.querySelectorAll('.play-buttons-container .guess');
  playButtons.forEach(button => {
    if (button.id === 'guess-albums') {
      button.value = 'GUESS ALBUMS';
    } else {
      button.value = "GUESS ARTISTS";
    }
    if (!(button.id === pressedButtonID)) {
      button.classList.remove('on');
    }
  })
}