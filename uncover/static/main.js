import {addTooltips, frequentElements, insertAfter, removeAllChildNodes,
        loadSpinner, fetchAvatar, fixInputData} from './utils.js'
import {AlbumGameInfo, Game, playInit} from "./game.js"
import {MusicFilter} from './musicFilter.js'
import {configureOptionsStyle, removePlayButtons, createPlayButtons,
        resetPlayButtons, createAvatarBox, removeAvatarContainer} from './uiconfig.js'
import {animateCoverArt, animateWaves, animatePlayButtons, animateAvatar, animateNavigationBar} from './animation.js'
import {loadCoverArt, loadFailureArt} from "./coverart.js";
import {createMusicInfoBox, removeMusicInfoBox} from "./albuminfobox.js";


let controller = null;

export const theGame = new Game(false);

export const albumGame = new AlbumGameInfo();

export const musicFilters = new MusicFilter({
  tags: ['hip-hop', 'jazz'],
  timeSpan: [1967, 2015]
})


// main submit function
export const submitInput = function(desiredMethod) {
  // remove unnecessary elements
  if (controller) {
    controller.abort();
  };
  controller = new AbortController();
  const signal = controller.signal;
  removePlayButtons();
  removeAvatarContainer();
  removeMusicInfoBox();
  theGame.uncoveryStatus = false;
  frequentElements.gameFrame.classList.remove('shadow-main');
  // empty html
  removeAllChildNodes(frequentElements.gameFrame);
  // add spinner while waiting for the response
  loadSpinner(frequentElements.gameFrame);
  // get stringified JSON body for the fetch function
  const body = prepareJSONBody(desiredMethod);
  // fetch!
  fetch(`${desiredMethod}`, {
    method: 'POST',
    signal: signal,
    headers: new Headers({
      'Content-Type': 'application/json'
    }),
    body: body
  })
  .then(response => {
  // if response is not ok (status ain't no 200)
    if (!response.ok) {
    // we get json with the 'failure' info
      const waves = document.querySelectorAll('.wave');
      waves.forEach(wave => wave.classList.add('falldown'));
      return response.json()
        .then(failData => {
          frequentElements.textField.classList.add("is-invalid");
          //val(failData.failDataJSON['message']); // show error message
          removeAllChildNodes(frequentElements.gameFrame);
          loadFailureArt(frequentElements.gameFrame, failData);
        });
    }
  return response.json();
  })
  .then(data => {
    /* storing album info in a global object */
    console.log(data);
    albumGame.albums = data['albums'];
    albumGame.currentQuery = data['info']['query'];
    albumGame.currentType = data['info']['type'];
    console.log(albumGame);
    // restores a 'valid' form style
    frequentElements.textField.classList.remove("is-invalid");
    // when done, removes current pictures from the frame, adds new ones
    // empty html
    removeAllChildNodes(frequentElements.gameFrame);
    /* adds a class 'loading' to block animation before all images are loaded */
    frequentElements.gameFrame.classList.add('loading');
    /* load/add cover art images */
    loadCoverArt(data);
    fixInputData(desiredMethod, data['info']['query']);
    /* add a progress bar */
    const progressBar = document.createElement("div");
    progressBar.id = "progress-bar";
    const referenceNode = document.querySelector(".search-and-options-container");
    insertAfter(progressBar, referenceNode);
    /* waiting for all images to load before showing them up*/
    console.log(document.querySelector('.avatar-container'));
    $('#game-frame').waitForImages(function() {
      //remove progress bar once loaded
      progressBar.remove();
      // remove 'loading' class that blocks animation of albums images
      this.classList.remove("loading");
      const itemsList = document.querySelectorAll(".flex-item");
      itemsList.forEach(item => {
        item.classList.add("loaded");
      });
      animateCoverArt();
      createPlayButtons(desiredMethod);
      const total = Math.min(albumGame.albums.length, 9);
      animatePlayButtons('.play-buttons-container .play-button', total);
      animateWaves(desiredMethod);
      const waves = document.querySelectorAll('.wave');
      waves.forEach(wave => wave.classList.remove('falldown'));
      downloadInit();
      playInit();
      createMusicInfoBox();
      if (desiredMethod === "by_lastfm_username") {
        // shows avatar if it's username method
        const username = data['info']['query'];
        fetchAvatar(username)
        .then(avatar => avatar['avatar'])
        .then(avatar => createAvatarBox(avatar, username))
        .then(() => {
          $('.wrapper')
          .waitForImages()
          .done(() => {
          animateAvatar(9);
//          document.querySelector('.avatar-container')
//            .classList.add('info-block-active');
          });
          }
        );
      };


    }, function(loaded, count, success) {
      /* animate progress bar */
      var bar1 = new ldBar("#progress-bar", {
        'preset': 'line'
      });
      bar1.set((loaded + 1 / count) * 100);
    });

  })
  .catch((error) => {
    // Handle the error
    console.log(`error is ${error}`);
  });
};

// event listener for a submit form and an 'ok' submit button
const submitForm = document.querySelector('#submit-form');
submitForm.addEventListener('submit', () => {
  // checks if the game is not on
  if (submitForm.id === 'submit-form') {
    const desiredMethod = document.querySelector('.method.active').id;
    submitInput(desiredMethod);
  }
});

// prepares stringified JSON body for the fetch function
function prepareJSONBody(method){
  let qualifier = '';
  let option = '';
  if (method === "explore") {
    // in case of 'explore' tab opened, get different values for the body
    qualifier = '';
    option = {
      "genres": musicFilters.tagsPickedInfo,
      "time_span": musicFilters.timeSpanInfo
    };
  } else {
    // get the input value
    qualifier = document.querySelector('#text-field').value;
    // get the option value from select menu
    option = frequentElements.selectOptions.value;
  };
  const body = {
    "qualifier": qualifier,
    "option": option
  };
  return JSON.stringify(body);
};

// initialize all the necessary download handlers
function downloadInit() {
  const downloadButton = document.querySelector('#download-button');
  downloadButton.addEventListener('click', () => {
    downloadButton.value = "WAIT FOR IT…";
    downloadButton.classList.add("wait-for-it");
    downloadButton.disabled = true;
    fetch("save_collage", {
      method: 'POST',
      headers: new Headers({
        'Content-Type': 'application/json'
      }),
      body: JSON.stringify({
        "images": albumGame.albums.map(album => album.image)
      })
    })
    .then(response => response.json()).then(data => {
      const myLink = document.createElement('a');
      myLink.href = data;
      myLink.target = "_blank";
      document.body.appendChild(myLink);
      myLink.click();
      downloadButton.value = "SAVE COLLAGE";
      downloadButton.classList.remove("wait-for-it");
      downloadButton.disabled = false;
    });
  });
};

const navBarSlideHandler = () => {
  const hamburgerMenu = document.querySelector('.hamburger-menu');
  const navigationBar = document.querySelector('.navigation-bar');
  hamburgerMenu.addEventListener("click", () => {
    navigationBar.classList.toggle('nav-active');
    hamburgerMenu.classList.toggle('hamburger-menu-active');
    if (navigationBar.classList.contains('nav-active')) {
      animateNavigationBar();
    }
  })
}

navBarSlideHandler();


const infoBlocksSlideHandler = () => {
  const toolIcon = document.querySelector('.tools-icon');
  toolIcon.addEventListener("click", () => {
    console.log('clicked!');
    const musicInfoBox = document.querySelector('.music-info-box');
    const musicGenresContainer = document.querySelector('.music-genres-container');
    const avatar = document.querySelector('.avatar-container');

    const exist = (element) => element;
    [musicInfoBox, musicGenresContainer, avatar].some(exist);
    console.log([musicInfoBox, musicGenresContainer, avatar].some(exist));
    if ([musicInfoBox, musicGenresContainer, avatar].some(exist)) {
      toolIcon.classList.toggle('tools-active');
    } else {
      toolIcon.classList.add('tools-active');
    }
    if (toolIcon.classList.contains('tools-active')) {
        [musicInfoBox, musicGenresContainer, avatar].forEach(item => {
      if (item) {
        item.classList.add('info-block-active');
      }
    });
    } else {
      [musicInfoBox, musicGenresContainer, avatar].forEach(item => {
      if (item) {
        item.classList.remove('info-block-active');
      }
    });
    };
  })

}
infoBlocksSlideHandler();

// activate buttons
const buttonsContainer = document.querySelector('#buttons-container');
// add an event listener to a buttons wrapper (event bubbling)
buttonsContainer.addEventListener('click', (event) => {
  const isButton = event.target.nodeName === 'INPUT';
  // check if a button was clicked, not the div
  if (!isButton) {
    return;
  };
  const targetButtonID = event.target.id;
  console.log(`event target: ${targetButtonID}`);
  console.log(frequentElements.activeButtonID());
  configureOptionsStyle(targetButtonID);
  const methodButtonsList = document.querySelectorAll(".method");
  methodButtonsList.forEach(button => button.classList.remove('active'));
  event.target.classList.add('active');
  const sliderContainer = document.querySelector('.slider-container');
  const musicGenresContainer = document.querySelector('.music-genres-container');
  if (!(event.target.id === "explore")) {
    if (sliderContainer) {
      sliderContainer.remove();
      musicGenresContainer.remove();
    };
    const tagsForm = document.querySelector('#tags-form');
    if (tagsForm) {
      tagsForm.id = 'submit-form';
    }
  };
});

/* displays 'options' menu when the input's focused  */
let timerID;
[frequentElements.textField, frequentElements.selectOptions].forEach(item => {
  item.addEventListener('focusin', () => {
    clearTimeout(timerID);
    // make sure the button's 'username' and the game is off
    if (
    (frequentElements.activeButtonID() === 'by_lastfm_username' || frequentElements.activeButtonID() === 'by_artist')
      && !(theGame.status)

    ) {
      frequentElements.selectOptions.style.display = 'block';
    };
  });
});

[frequentElements.textField, frequentElements.selectOptions].forEach(item => {
  item.addEventListener('focusout', () => {
    timerID = setTimeout(function() {
      $(".select-options").hide();
  }, 10);
  });
});


// initialize/create the tooltips
addTooltips();
