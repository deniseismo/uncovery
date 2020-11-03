import {frequentElements, removeAllChildNodes, insertAfter} from './utils.js'
import {cancelGame} from './game.js'
import {prepareToExplore, cleanAfterExplore} from './explore.js'
import {renderAboutPage} from './about.js';
import {theGame} from "./main.js";

export function hideOptions() {
  const sliderContainer = document.querySelector('.slider-container');
  const scoreContainer = document.querySelector('.score-container');
  [frequentElements.selectOptions, sliderContainer, scoreContainer]
    .forEach(container => {
      if (container) {
        container.style.display = 'none';
      };
    });
};

export function configureOptionsStyle(targetButtonID) {
  // if a button pressed is a new button/new destination
  if (targetButtonID !== frequentElements.activeButtonID()) {
    setSelectOptions(targetButtonID);
    // cancel the game
    if (theGame.status) {
      const currentButton = document.querySelector('.play-button.on');
      cancelGame(currentButton);
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
    if (targetButtonID === "by_spotify") {
      prepareSpotify();
    } else if (frequentElements.activeButtonID() === "by_spotify") {
      cleanAfterSpotify();
    }

    // change the placeholder to the correct one
    setPlaceholder(targetButtonID);
    setCurrentPageTitle(targetButtonID);
    frequentElements.textField.value = '';
  }
};


function prepareSpotify() {
  const okButton = document.querySelector('.ok-btn');
  okButton.value = 'GET YOUR FAVORITES';
  okButton.style.width = '100%';
  const inputField = document.querySelector('.text-field-container');
  inputField.style.display = 'none';
}

function cleanAfterSpotify() {
  const okButton = document.querySelector('.ok-btn');
  okButton.value = 'OK';
  okButton.style.width = 'auto';
  const inputField = document.querySelector('.text-field-container');
  inputField.style.display = 'flex';
}



function setCurrentPageTitle(buttonID) {
  const theButton = document.getElementById(buttonID);
  const title = theButton.value;
  const currentPageTitle = document.querySelector('.current-page-title');
  currentPageTitle.textContent = `/${title}`;
}


function setSelectOptions(targetButtonID) {
  removeAllChildNodes(frequentElements.selectOptions)
  function createOption(value, text, selected=false) {
    const option = document.createElement("option");
    option.value = value;
    option.text = text;
    option.selected = selected;
    return option;
  }
  if (targetButtonID === "by_lastfm_username") {
    const sevenDays = createOption("7day", "7 days");
    const threeMonths = createOption("3month", "3 months");
    const twelveMonths = createOption("12month", "1 year");
    const overall = createOption("overall", "All-time", true);
    const shuffle = createOption("shuffle", "Shuffle");
    [sevenDays, threeMonths, twelveMonths, overall, shuffle].forEach(option => {
      frequentElements.selectOptions.appendChild(option);
    });
  } else if (targetButtonID === "by_artist") {
    const popular = createOption("popular", "Popular", true);
    const shuffle = createOption("shuffle", "Shuffle");
    const latest = createOption("latest", "Latest");
    const oldest = createOption("earliest", "Earliest");
    [popular, shuffle, latest, oldest].forEach(option => {
      frequentElements.selectOptions.appendChild(option);
    });
  };
}

export function setPlaceholder(targetButtonID) {
  const options = {
    "by_lastfm_username": "last.fm username",
    "by_artist": "artist name",
    "by_spotify": "Spotify Playlist Link",
    "explore": "music tags/genres: up to three tags"
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

export function createAvatarBox(avatarURL, username) {
  if (!(avatarURL)) {
    return false;
  }
  console.log(avatarURL);
  const avatarContainer = document.createElement('div');
  avatarContainer.classList.add('avatar-container', 'shadow-main');
  const userName = document.createElement('p');
  userName.classList.add('username');
  userName.textContent = username;
  const avatarImage = document.createElement('img');
  avatarImage.classList.add("avatar-image");
  avatarImage.src = avatarURL;
  avatarContainer.appendChild(userName);
  avatarContainer.appendChild(avatarImage);
  document.querySelector('.wrapper').appendChild(avatarContainer);
}

export function removeAvatarContainer() {
  const avatarContainer = document.querySelector('.avatar-container');
  if (avatarContainer) {
    avatarContainer.remove();
  }
}

//export showToolsIcon() {
//  const avatarContainer = document.querySelector('.avatar-container');
//  const musicGenresContainer = document.querySelector('.music-genres-container');
//  const musicInfoBox = document.querySelector('.music-info-box');
//  [avatarContainer, musicGenresContainer
//}
//
