import {frequentElements} from './utils.js'
import {cancelGame} from './game.js'
import {prepareToExplore, cleanAfterExplore} from './explore.js'

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

export function setPlaceholder(targetButtonID) {
  const options = {
    "by_username": "last.fm username",
    "by_artist": "artist name",
    "by_spotify": "Spotify Playlist Link",
    "explore": "music tags/genres"
  }
  frequentElements.textField.placeholder = options[targetButtonID];
};