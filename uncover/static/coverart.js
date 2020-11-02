import {frequentElements, insertAfter} from "./utils.js"

// loads cover art images to the main game frame
export function loadCoverArt(data) {
  const totalAmountOfAlbums = data['albums'].length;
  let length = Math.min(totalAmountOfAlbums, 9);
  for (let i = 0; i < length; i++) {
    const album = data['albums'][i];
    const imageURL = data['albums'][i]['image'];
    const id = data['albums'][i]['id']
    const coverArt = document.createElement("img");
    coverArt.classList.add(`art-${id}`);
    coverArt.classList.add('cover-art');
//    coverArt.src = `${imageURL}`;
    coverArt.alt = "album cover art";
    const successIcon = document.createElement('img');
    successIcon.id = `success-${id}`;
    successIcon.classList.add('success-icon');
    successIcon.src = 'static/images/check-mark-contrast.png';
    successIcon.alt = 'checkmark';
    const flexItem = document.createElement('div');
    flexItem.id = `item-${i}`;
    flexItem.classList.add('flex-item');
    flexItem.appendChild(coverArt);
    flexItem.appendChild(successIcon);
    frequentElements.gameFrame.appendChild(flexItem);
  }
  resizeCoverArtImages(data, length);
};

function resizeCoverArtImages(data, amountOfAlbums) {
  const allCoverArtElements = document.querySelectorAll('.cover-art');
  console.log(amountOfAlbums);
  switch (amountOfAlbums) {
    case 3:
    case 6:
    case 9:
      for (let i = 0; i < allCoverArtElements.length; i++) {
        let imageURL = data['albums'][i]['image'];
        if (data['albums'][i].hasOwnProperty('image_small')) {
          imageURL = data['albums'][i]['image_small'];
        }
        allCoverArtElements[i].src = `${imageURL}`;
      }
      break;
    case 1:
      allCoverArtElements[0].classList.add('cover-big');
      const imageURL = data['albums'][0]['image'];
      allCoverArtElements[0].src = `${imageURL}`;
      break;
    case 2:
    case 4:
      for (let i = 0; i < allCoverArtElements.length; i++) {
        let imageURL = data['albums'][i]['image'];
        if (data['albums'][i].hasOwnProperty('image_medium')) {
          imageURL = data['albums'][i]['image_medium'];
        }
        allCoverArtElements[i].classList.add('cover-medium');
        allCoverArtElements[i].src = `${imageURL}`;
      }
      break;
    case 5:
    case 8:
      [document.querySelector(".art-0"), document.querySelector(".art-1")]
        .forEach((image, i) => {
          let imageURL = data['albums'][i]['image'];
          if (data['albums'][i].hasOwnProperty('image_medium')) {
            imageURL = data['albums'][i]['image_medium'];
          }
          image.classList.add('cover-medium');
          image.src = `${imageURL}`;
        });
      for (let i = 2; i < allCoverArtElements.length; i++) {
        let imageURL = data['albums'][i]['image'];
          if (data['albums'][i].hasOwnProperty('image_small')) {
            imageURL = data['albums'][i]['image_small'];
          }
          allCoverArtElements[i].src = `${imageURL}`;
      }
      break;
    case 7:
      [document.querySelector(".art-0"), document.querySelector(".art-1"),
      document.querySelector(".art-2")]
        .forEach((image, i) => {
          let imageURL = data['albums'][i]['image'];
          if (data['albums'][i].hasOwnProperty('image_medium')) {
            imageURL = data['albums'][i]['image_medium'];
          }
          image.classList.add('cover-medium');
          image.src = `${imageURL}`;
        });

      [document.querySelector(".art-3"), document.querySelector(".art-4"),
      document.querySelector(".art-5"), document.querySelector(".art-6")]
        .forEach((image, i) => {
          image.classList.add('cover-small');
          let imageURL = data['albums'][i + 3]['image'];
          if (data['albums'][i + 3].hasOwnProperty('image_small')) {
            imageURL = data['albums'][i + 3]['image_small'];
          }
          image.src = `${imageURL}`;
        });
      const referenceNode = document.querySelector('#item-2');
      const specialContainer = document.createElement('div');
      specialContainer.classList.add('seven-albums-special-container');
      insertAfter(specialContainer, referenceNode);
      [document.querySelector("#item-3"), document.querySelector("#item-4"),
        document.querySelector("#item-5"), document.querySelector("#item-6")]
        .forEach((item) => specialContainer.appendChild(item));
      break;
  }
};

export function loadFailureArt(node, failData) {
  frequentElements.gameFrame.classList.add("shadow-main");
  const failureArt = document.createElement("img");
  const failureArtURL = failData['failure_art'];
  const failureMessage = failData['message'];
  failureArt.src = failureArtURL;
  failureArt.classList.add("failure-art");

  const failureArtBlock = document.createElement("div");
  failureArtBlock.classList.add("failure-art-block", "shadow-main");

  const failureArtText = document.createElement("h1");
  failureArtText.classList.add("text-light");
  failureArtText.textContent = failureMessage;

  failureArtBlock.appendChild(failureArtText);

  node.appendChild(failureArt);
  node.appendChild(failureArtBlock);
};