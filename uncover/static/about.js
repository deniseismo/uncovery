import {frequentElements, removeAllChildNodes, insertAfter} from './utils.js'
import {animateAboutItems} from "./animation.js";
import {removePlayButtons, removeAvatarContainer} from "./uiconfig.js";

export function renderAboutPage() {
  // empty html
  removeAllChildNodes(frequentElements.gameFrame);
  removeAvatarContainer();
  removePlayButtons();
  const searchBar = document.querySelector(".search-and-options-container");
  searchBar.style.display = 'none';
  for (let i = 1; i < 10; i++) {
    const frameItem = document.createElement('div');
    frameItem.id = `about-${i}`;
    frameItem.classList.add('about-item', "shadow-main");
    const centerCircle = document.createElement('div');
    centerCircle.classList.add('center-circle');
    frameItem.appendChild(centerCircle);
    frequentElements.gameFrame.appendChild(frameItem);
  }
  addAboutText();
  animateAboutItems();
}

function addAboutText() {
  const aboutText = document.createElement('div');
  aboutText.classList.add('about-text');

  const createdBy = document.createElement('p');
  createdBy.classList.add('created-by');
  const thanks = document.createElement('p');
  thanks.classList.add('thanks');
  const forWhat = document.createElement('p');
  forWhat.classList.add('for-what');
  const ifYouLike = document.createElement('p');
  ifYouLike.classList.add('if-you-like');


  createdBy.textContent = "Created by Denis Kostarev";
  thanks.textContent = "Thanks to The MetaBrainz Foundation, Discogs, and Last.fm";
  forWhat.textContent = "for their immense databases.";
  ifYouLike.textContent = "If you like this project, consider supporting it";


  aboutText.appendChild(createdBy);
  aboutText.appendChild(thanks);
  aboutText.appendChild(forWhat);
  aboutText.appendChild(ifYouLike);


  frequentElements.gameFrame.appendChild(aboutText);
}


