import {frequentElements, removeAllChildNodes, insertAfter} from './utils.js'
import anime from './anime.es.js'

export function renderAboutPage() {
  // empty html
  removeAllChildNodes(frequentElements.gameFrame);
  frequentElements.playButton.classList.remove("visible");
  frequentElements.downloadButton.classList.remove("visible");
  const searchBar = document.querySelector(".search-and-options-container");
  searchBar.style.display = 'none';
  for (let i = 1; i < 10; i++) {
    const frameItem = document.createElement('div');
    frameItem.id = `about-${i}`;
    frameItem.classList.add('about-item', "shadow-main");
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


function animateAboutItems() {
  anime({
    targets: '.about-item',
    scale: [
      {value: 0.5, easing: 'easeInOutQuad', duration: 50},
      {value: 1, easing: 'easeInOutQuad', duration: 100}
    ],
    opacity: [0, 0.5],
    borderRadius: ['100%', '0%'],
    delay: anime.stagger(110, {easing: 'easeOutQuad'})
  });
  anime({
    targets: ".about-text p",
    backgroundColor: ["#FFF", "#005191"],
    scale: [2, 1],
    opacity: [0.5, 1],
    delay: anime.stagger(110, {easing: 'easeOutQuad'})
  });
};