import {frequentElements, removeAllChildNodes, insertAfter} from './utils.js'
import {animateAboutItems} from "./animation.js";
import {removePlayButtons, removeAvatarContainer} from "./uiconfig.js";
import {removeMusicInfoBox} from "./albuminfobox.js";

// renders About 'Chapter'
export function renderAboutPage() {
  // remove unnecessary elements
  removeAllChildNodes(frequentElements.gameFrame);
  removeAvatarContainer();
  removePlayButtons();
  removeMusicInfoBox();
  const searchBar = document.querySelector(".search-and-options-container");
  searchBar.style.display = 'none';
  // display 'vinyl' blocks
  for (let i = 1; i < 10; i++) {
    const frameItem = document.createElement('div');
    frameItem.id = `about-${i}`;
    frameItem.classList.add('about-item', "shadow-main");
    // add circles inside vinyls
    const centerCircle = document.createElement('div');
    centerCircle.classList.add('center-circle');
    frameItem.appendChild(centerCircle);
    frequentElements.gameFrame.appendChild(frameItem);
  }
  // adds text
  addAboutText();
  // animate everything
  animateAboutItems();
};

// adds About page text
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
  thanks.textContent = "A huge thanks goes out to The MetaBrainz Foundation, Last.fm, Discogs, and Spotify";
  forWhat.textContent = "for their incredible resources.";
  ifYouLike.textContent = "If you like this project, consider supporting it";

  aboutText.appendChild(createdBy);
  aboutText.appendChild(thanks);
  aboutText.appendChild(forWhat);
  aboutText.appendChild(ifYouLike);

  frequentElements.gameFrame.appendChild(aboutText);
}


