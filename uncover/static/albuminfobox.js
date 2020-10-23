import {theGame, albumGame} from "./main.js"
import {animateMusicGenresContainer, animatePlayButtons} from './animation.js'
import {handleTags} from "./explore.js"


export function createMusicInfoBox() {
  const musicInfoBox = document.createElement('div');
  musicInfoBox.classList.add('music-info-box', 'shadow-main');
  const infoText = document.createElement('h1');
  infoText.textContent = "ALBUM INFO";
  const uncover = document.createElement('input');
  uncover.id = 'uncover-info';
  uncover.type = 'submit';
  uncover.value = "UNCOVER";
  uncover.classList.add('btn', 'button', 'shadow-main', 'play-button', 'visible');
  uncover.addEventListener('click', uncoverModeOn);
  const description = document.createElement("p");
  description.classList.add('info-box-description');
  description.textContent = "I ain't playing, I really need to know what these albums are!";
  const albumInfoCard = createAlbumInfoCard();
  musicInfoBox.appendChild(infoText);
  musicInfoBox.appendChild(description);
  musicInfoBox.appendChild(uncover);
  musicInfoBox.appendChild(albumInfoCard);
  document.querySelector('main').appendChild(musicInfoBox);
  animateMusicGenresContainer(musicInfoBox);
  animatePlayButtons(uncover, 1);
}

function uncoverModeOn() {
  theGame.uncoveryStatus = true;
  const uncoverButton = document.getElementById("uncover-info");
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

function removeInfoBoxDescription() {
  const infoBoxDescription = document.querySelector('.info-box-description');
  if (infoBoxDescription) {
    infoBoxDescription.style.display = 'none';
  }
}

function updateInfoBoxDescription(text) {
  const infoBoxDescription = document.querySelector('.info-box-description');
  if (infoBoxDescription) {
    infoBoxDescription.style.display = 'block';
    infoBoxDescription.textContent = text;
  }
}


function uncoverAlbumInfo(album) {
  const albumInfoCard = document.querySelector('.album-info-card');
  albumInfoCard.style.display = 'flex';
  const albumName = document.querySelector('.album-name-info');
  albumName.textContent = album.title;
  albumName.classList.add('shadow-main');
  if (!(albumGame.currentType === 'artist')) {
    const by = document.querySelector('.by');
    by.textContent = 'by';
    const artistName = document.querySelector('.artist-name-info');
    artistName.textContent = album.artist_name;
  }
  const year = document.querySelector('.year');
  if (album.year) {
    year.textContent = `(${album.year})`;
  };
}


function createAlbumInfoCard() {
  const albumName = document.createElement('p');
  albumName.classList.add('album-name-info');
  const by = document.createElement('p');
  by.classList.add('by');
  const artistName = document.createElement('p');
  artistName.classList.add('artist-name-info');
  const year = document.createElement('p');
  year.classList.add('year');
  const albumInfoCard = document.createElement('div');
  albumInfoCard.classList.add('album-info-card');
  [albumName, by, artistName, year].forEach(item => albumInfoCard.appendChild(item));
  return albumInfoCard;
}


export function removeMusicInfoBox() {
  const musicInfoBox = document.querySelector('.music-info-box');
  if (musicInfoBox) {
    musicInfoBox.remove();
  }
}

export function hideUncoverModeForGame() {
  const albumInfoCard = document.querySelector('.album-info-card');
  albumInfoCard.style.display = 'none';
  const uncoverButton = document.getElementById("uncover-info");
  uncoverButton.style.display = 'none';
  updateInfoBoxDescription("Game is on. No peeking!");
  const albumItems = document.querySelectorAll('.flex-item');
  albumItems.forEach(item => {
    item.classList.remove('uncoverable');
  });
}

export function backToRealityFromTheGame() {
  console.log('canceled but explore')
  const formField = document.querySelector('.form-field');
  const activeButton = document.querySelector('.method.active');
  if (activeButton === 'explore') {
    formField.addEventListener("input", handleTags);
    $('.form-field').autocomplete('enable');
  }
  const sliderContainer = document.querySelector('.slider-container');
  const albumItems = document.querySelectorAll('.flex-item');
  if (theGame.uncoveryStatus) {
    updateInfoBoxDescription("Snap back to reality! You can now safely peek at cover arts.");
    albumItems.forEach(item => {
    item.classList.add('uncoverable');
  });
  } else {
    updateInfoBoxDescription("I ain't playing, I really need to know what these albums are!");
    const uncoverButton = document.getElementById("uncover-info");
    uncoverButton.style.display = 'block';
  }

  if (sliderContainer) {
    sliderContainer.style.display = 'flex';
  };
}