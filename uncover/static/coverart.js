import {frequentElements} from "./utils.js"

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
    coverArt.src = `${imageURL}`;
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
  resizeCoverArtImages(length);
};

function resizeCoverArtImages(amountOfAlbums) {
  console.log(amountOfAlbums);
  switch (amountOfAlbums) {
    case 1:
      const albumImage = document.querySelector(".cover-art");
      albumImage.classList.add('cover-big');
      break;
    case 2:
    case 4:
      const albumImagesList = document.querySelectorAll(".cover-art");
      albumImagesList.forEach((image) => image.classList.add('cover-medium'));
      break;
    case 5:
    case 8:
      console.log(document.querySelector('.art-0'), document.querySelector('.art-1'));
      [document.querySelector(".art-0"), document.querySelector(".art-1")]
        .forEach((image) => image.classList.add('cover-medium'));
      break;
    case 7:
      [document.querySelector(".art-0"), document.querySelector(".art-1"),
      document.querySelector(".art-2")]
        .forEach((image) => image.classList.add('cover-medium'));

      [document.querySelector(".art-3"), document.querySelector(".art-4"),
      document.querySelector(".art-5"), document.querySelector(".art-6")]
        .forEach((image) => image.classList.add('cover-small'));
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
  failureArt.src = failureArtURL;
  failureArt.classList.add("failure-art");

  const failureArtBlock = document.createElement("div");
  failureArtBlock.classList.add("failure-art-block", "shadow-main");

  const failureArtText = document.createElement("h1");
  failureArtText.classList.add("text-light");
  failureArtText.textContent = "someone made an oopsie!";

  failureArtBlock.appendChild(failureArtText);

  node.appendChild(failureArt);
  node.appendChild(failureArtBlock);
};