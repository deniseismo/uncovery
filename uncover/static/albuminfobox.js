import {theGame, albumGame, mediaQuery, handleToolsIconChange} from "./main.js"
import {animateMusicGenresContainer, animatePlayButtons, animateSpotifyWidget} from './animation.js'
import {handleTags} from "./explore.js"
import {loadSpinner, insertAfter} from "./utils.js"
import {showToolsIcon} from "./uiconfig.js"



// creates an info box with all the info about album clicked
export function createMusicInfoBox() {
  const musicInfoBox = document.createElement('div');
  musicInfoBox.classList.add('music-info-box', 'shadow-main');
  const infoText = document.createElement('h1');
  infoText.textContent = "ALBUM INFO";
  infoText.classList.add('album-info-header');
  const uncover = document.createElement('input');
  uncover.id = 'uncover-info';
  uncover.type = 'submit';
  uncover.value = "UNCOVER";
  uncover.classList.add('btn', 'button', 'shadow-main', 'play-button', 'visible');
  uncover.addEventListener('click', uncoverModeOn);
  const description = document.createElement("p");
  description.classList.add('info-box-description', 'no-margin');
  description.textContent = "I ain't playing, I really need to know what these albums are!";
  // get album info card
  const albumInfoCard = createAlbumInfoCard();
  // get spotify widget
  const spotifyWidget = createSpotifyWidget();
  musicInfoBox.appendChild(infoText);
  musicInfoBox.appendChild(description);
  musicInfoBox.appendChild(uncover);
  musicInfoBox.appendChild(albumInfoCard);
  musicInfoBox.appendChild(spotifyWidget);
  document.querySelector('.wrapper').appendChild(musicInfoBox);
  animateMusicGenresContainer(musicInfoBox);
  animatePlayButtons(uncover, 1);
  // triggers a function that may or may not (depends on view-size) display a tools icon
  showToolsIcon();
}


// a function that makes all cover art images clickable and uncoverable
function uncoverModeOn() {
  theGame.uncoveryStatus = true;
  const uncoverButton = document.getElementById("uncover-info");
  // remove 'uncover' button
  uncoverButton.style.display = 'none';
  updateInfoBoxDescription("Now all cover arts are ready for uncovery. Click'em away!");
  const albumItems = document.querySelectorAll('.flex-item');
  albumItems.forEach(item => {
    item.addEventListener('click', () => {
      if (!(theGame.status)) {
        removeInfoBoxDescription();
        const id = item.id[item.id.length - 1];
        uncoverAlbumInfo(albumGame.albums[id]);
      };
    });
    item.classList.add('uncoverable');
  })
}

// removes an 'instruction' for the info box
function removeInfoBoxDescription() {
  const infoBoxDescription = document.querySelector('.info-box-description');
  if (infoBoxDescription) {
    infoBoxDescription.style.display = 'none';
  }
}

// updates an 'instruction' for the info box
function updateInfoBoxDescription(text) {
  // change instruction text to the text provided
  const infoBoxDescription = document.querySelector('.info-box-description');
  if (infoBoxDescription) {
    infoBoxDescription.style.display = 'block';
    infoBoxDescription.textContent = text;
  }
}

// fetch album's spotify ID
async function fetchAlbumID(albumName, artistName) {
  // fetches current tags list
  const response = await fetch('fetch_album_id', {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({
      "album_name": albumName,
      "artist_name": artistName
    })
  });
  if (!response.ok) {
    return null;
  }
  const albumID = await response.json();
  return albumID;
};


// show current album (on click) info in the album info box
function uncoverAlbumInfo(album) {
  const artistJke = album.artist_name
  const albumJke = album.title
  const albumInfoCard = document.querySelector('.album-info-card');
  albumInfoCard.style.display = 'flex';
  const albumName = document.querySelector('.album-name-info');
  albumName.textContent = album.title;
  albumName.classList.add('shadow-main');
  if (!(albumGame.currentType === 'artist')) {
    // show artist's name (by 'artist_name') if it not artist's mode ('cause it's redundant)
    const by = document.querySelector('.by');
    by.textContent = 'by';
    const artistName = document.querySelector('.artist-name-info');
    artistName.textContent = album.artist_name;
  }
  const year = document.querySelector('.year');
  if (album.year) {
    // show album's release date
    year.textContent = `(${album.year})`;
  };
  // get album's spotify id
  fetchAlbumID(album.title, artistJke).then(data => {
    if (data) {
        const albumID = data['album_id']
        console.log('spotify! ura!')
        spotifyLoadingSpinner();
        const spotifyWidget = document.querySelector('.spotify-widget');
        spotifyWidget.src = `https://open.spotify.com/embed/album/${albumID}`;
        // register onload spotify handler
        spotifyWidget.onload = showSpotifyOnLoad;
        // register onerror spotify handler
        spotifyWidget.onerror = function() {
          hideSpotifyWidget();
          console.log("something's wrong with the iframe");
        };
        const musicInfoBox = document.querySelector('.music-info-box');
        musicInfoBox.classList.add('no-bottom-padding');
    }
    else {
        hideSpotifyWidget();
    }
  })
}

// hides spotify widget in case of errors or if no album id was found
function hideSpotifyWidget() {
    const spotifyWidget = document.querySelector('.spotify-widget');
    spotifyWidget.classList.remove('spotify-active');
    const widgetWrapper = document.querySelector('.widget-wrapper');
    widgetWrapper.style.display = 'none';
    const musicInfoBox = document.querySelector('.music-info-box');
    musicInfoBox.classList.remove('no-bottom-padding');
}

// creates an appropriate iframe for the spotify widget
function createSpotifyWidget() {
  const iFrame = document.createElement('iframe');
  iFrame.classList.add('spotify-widget');
  iFrame.src = '';
  iFrame.width = '100%';
  iFrame.height = '300px';
  iFrame.frameborder = '0';
  iFrame.allowtransparency = 'true';
  iFrame.allow = "encrypted-media";
  const widgetWrapper = document.createElement('div');
  widgetWrapper.classList.add('widget-wrapper');
  widgetWrapper.style.display = 'none';
  widgetWrapper.appendChild(iFrame);
  return widgetWrapper;
}

// show loading spinner while getting spotify info
function spotifyLoadingSpinner() {
  const spinnerExists = document.querySelector('.spotify-spinner-container');
  if (spinnerExists) {
    return;
  }
  const spotifySpinnerContainer = document.createElement('div');
  spotifySpinnerContainer.classList.add('spotify-spinner-container');
  const loadingMessage = document.createElement('p');
  loadingMessage.classList.add('spotify-loading-message', 'no-margin');
  loadingMessage.textContent = 'fetching Spotify magic…';
  spotifySpinnerContainer.appendChild(loadingMessage);
  loadSpinner(spotifySpinnerContainer);
  const albumInfoCard = document.querySelector('.album-info-card');
  insertAfter(spotifySpinnerContainer, albumInfoCard);
}

// show spotify widget/container when widget successfully fetched all the necessary data
function showSpotifyOnLoad() {
  const spotifySpinnerContainer = document.querySelector('.spotify-spinner-container');
  if (spotifySpinnerContainer) {
    spotifySpinnerContainer.remove();
  }
  const spotifyWidget = document.querySelector('.spotify-widget');
  console.log(spotifyWidget)
  console.log(spotifyWidget.classList)
  if (!(spotifyWidget.classList.contains('spotify-active'))) {
    animateSpotifyWidget();
    spotifyWidget.classList.add('spotify-active');
  }
  const widgetWrapper = document.querySelector('.widget-wrapper');
  // TODO: show animation only no iframe was present
  widgetWrapper.style.display = 'flex';
}

// create a container for album info (title, artist, year)
function createAlbumInfoCard() {
  const albumName = document.createElement('p');
  albumName.classList.add('album-name-info');
  const by = document.createElement('p');
  by.classList.add('by', 'no-margin');
  const artistName = document.createElement('p');
  artistName.classList.add('artist-name-info', 'no-margin');
  const year = document.createElement('p');
  year.classList.add('year', 'no-margin');
  const albumInfoCard = document.createElement('div');
  albumInfoCard.classList.add('album-info-card');
  [albumName, by, artistName, year].forEach(item => albumInfoCard.appendChild(item));
  return albumInfoCard;
}

// removes album info box altogether
export function removeMusicInfoBox() {
  const musicInfoBox = document.querySelector('.music-info-box');
  if (musicInfoBox) {
    musicInfoBox.remove();
  }
}

// hide album info when the game is on (without deleting the music info box container)
export function hideUncoverModeForGame() {
  const albumInfoCard = document.querySelector('.album-info-card');
  albumInfoCard.style.display = 'none';
  const uncoverButton = document.getElementById("uncover-info");
  uncoverButton.style.display = 'none';
  const widgetWrapper = document.querySelector('.widget-wrapper');
  widgetWrapper.style.display = 'none';
  const musicInfoBox = document.querySelector('.music-info-box');
  musicInfoBox.classList.remove('no-bottom-padding');
  updateInfoBoxDescription("Game is on. No peeking!");
  const albumItems = document.querySelectorAll('.flex-item');
  albumItems.forEach(item => {
    item.classList.remove('uncoverable');
  });
}

// gets all the necessary info containers back
export function backToRealityFromTheGame() {
  console.log('canceled but explore')
  const formField = document.querySelector('.form-field');
  const activeButton = document.querySelector('.method.active');
  if (activeButton.id === 'explore') {
    console.log('yeah boy!');
    // makes tags uncoverable again
    formField.addEventListener("input", handleTags);
    formField.id = "tag-field";
    $('.form-field').autocomplete('enable');
  }
  const sliderContainer = document.querySelector('.slider-container');
  const albumItems = document.querySelectorAll('.flex-item');
  if (theGame.uncoveryStatus) {
    // makes albums uncoverable
    updateInfoBoxDescription("Snap back to reality! You can now safely peek at cover arts.");
    albumItems.forEach(item => {
    item.classList.add('uncoverable');
  });
  } else {
    // returns the initial instruction message for the user
    updateInfoBoxDescription("I ain't playing, I really need to know what these albums are!");
    const uncoverButton = document.getElementById("uncover-info");
    uncoverButton.style.display = 'block';
  }

  if (sliderContainer) {
    // returns the slider container (time span)
    sliderContainer.style.display = 'flex';
  };
}