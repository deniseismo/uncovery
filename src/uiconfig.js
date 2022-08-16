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
      removePlayButtons();
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
    showOrHideToolsIcon();
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
  const alreadyExists = document.querySelector('.play-buttons-container');
  if (alreadyExists) {
    return;
  }
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
  showToolsIcon();
}

export function removeAvatarContainer() {
  const avatarContainer = document.querySelector('.avatar-container');
  if (avatarContainer) {
    avatarContainer.remove();
  }
}


function showOrHideToolsIcon() {
    const musicInfoBox = document.querySelector('.music-info-box');
    const musicFiltersContainer = document.querySelector('.music-filters-container');
    const avatar = document.querySelector('.avatar-container');

    const exist = (element) => element;
    if ([musicInfoBox, musicFiltersContainer, avatar].some(exist)) {
        console.log('some exist')
        showToolsIcon();
    }
    else {
      console.log('some do not exist')
      const toolsIcon = document.querySelector('.tools-icon')
      toolsIcon.style.display = 'none';
    }
}


export function showToolsIcon() {
    const mediaQuery = window.matchMedia('(min-width: 800px)')

// Check if the media query is true
    if (!mediaQuery.matches) {
      // Then trigger an alert
      const toolsIcon = document.querySelector('.tools-icon')
      toolsIcon.style.display = 'block';
    }
}

export function getCancelIconSvg(queryElement) {
  const cancelIcon = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  cancelIcon.xmlns = "http://www.w3.org/2000/svg";
  cancelIcon.classList.add('album-info-cancel-icon');
  cancelIcon.setAttribute('viewBox', '0 0 512 512');
  const title = document.createElement('title');
  title.textContent = 'Close';
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute('fill', 'none');
  path.setAttribute('stroke', 'currentColor');
  path.setAttribute('stroke-linejoin', 'round');
  path.setAttribute('stroke-width', '32');
  path.setAttribute('d', 'M368 368L144 144M368 144L144 368');
  path.classList.add('cancel-icon-path');
  cancelIcon.appendChild(title);
  cancelIcon.appendChild(path);
  cancelIcon.addEventListener('click', () =>  {
    const musicInfoBox = document.querySelector(queryElement);
    musicInfoBox.classList.remove('info-block-active');
    musicInfoBox.classList.add('info-block-hidden');
    if (queryElement === '.music-filters-container') {
      const toolsIcon = document.querySelector('.tools-icon');
         if (toolsIcon) {
           if (!toolsIcon.classList.contains('tools-active')) {
            toolsIcon.classList.add('tools-active');
            }
         }
    }
  });
  return cancelIcon;
}
