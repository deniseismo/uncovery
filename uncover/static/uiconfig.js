import {frequentElements, removeAllChildNodes} from './utils.js'
import {cancelGame} from './game.js'
import {prepareToExplore, cleanAfterExplore} from './explore.js'
import {renderAboutPage} from './about.js';

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