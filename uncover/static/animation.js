import anime from './anime.es.js'
import {Wave, Blob} from './shapes.js'

// main animation function for all cover art images
export function animateCoverArt() {
  anime({
    targets: '.cover-art',
    scale: [
      {value: 0.5, easing: 'easeInOutQuad', duration: 50},
      {value: 1, easing: 'easeInOutQuad', duration: 100}
    ],
    opacity: [0, 1],
    delay: anime.stagger(110, {easing: 'easeOutQuad'})
  });
};

// animates waves randomly using Wave class
export function animateWaves(method) {
  // create an instance of Wave class
  const theWave = new Wave(method);

  anime({
    targets: '#wave-path-3',
    d: [
      {
        // get random shape
        value: theWave.getWave()['d'],
        duration: 300,
        easing: 'easeInOutBack'
      }
    ],
    // get particular color (depends on 'method')
    fill: theWave.getWave()['fill']
  });
};

// animates time span numbers change (e.g. 1960 - 2015)
export function animateTimeSpan(timeBefore, timeAfter) {
  if (timeBefore[0] !== timeAfter[0]) {
    anime({
      targets: '.time-span-begin',
      textContent: [timeBefore[0], timeAfter[0]],
      round: 1,
      duration: 500
    });
  };
  if (timeBefore[1] !== timeAfter[1]) {
    anime({
      targets: '.time-span-end',
      textContent: [timeBefore[1], timeAfter[1]],
      round: 1,
      duration: 500,
      easing: 'linear'
    });
  };
};

// animates music genre appearance
export function animateMusicGenreOn(musicGenreElement) {
  console.log('genre show up!', musicGenreElement)
  anime({
    targets: musicGenreElement,
    scale: [5, 1],
    translateY: [150, 0],
    opacity: [0, 1],
    duration: 300
  });
};

// animates any sort of block disappearance (e.g. music genre)
export function animateBlockOff(block) {
  console.log(`animating! ${block}`)
  anime({
    targets: block,
    scale: [10, 0],
    translateY: [0, 50],
    opacity: [1, 0],
    duration: 150,
    backgroundColor: "#ed6663"
  });
};

// shows blinking animation for the guessed albums
export function animateHighlightGuessedAlbum(album) {
  anime({
    targets: album,
    opacity: [
      {value: 0.3, easing: 'easeOutElastic(5, 0.3)', duration: 200},
      {value: 1, easing: 'easeOutElastic(5, 0.3)', duration: 400}
    ]
  });
};

// animates appearance of a music genres container
export function animateMusicGenresContainer(container) {
  anime({
    targets: container,
    scale: [0.5, 1],
    translateY: [50, 0],
    opacity: [0, 1],
    borderRadius: ['200px', '0px'],
    duration: 700
  });
}

// animates a random winning message
export function animateWinningMessage() {
  let tl = anime.timeline({
  easing: 'easeOutExpo',
  duration: 750,
  });
  tl
  .add({
      targets: '.winning-text',
    opacity: [
      {value: 0, easing: 'easeOutExpo'},
      {value: 1, easing: 'easeOutExpo'},
      {value: 0, easing: 'easeOutElastic(5, 0.3)'},
      {value: 1, easing: 'linear'}
    ],
    scale: [
      {value: 0.8, easing: 'easeOutExpo'},
      {value: 1.5, delay: 500},
      {value: 1, duration: 500}
    ],
    fontSize: ['0.1rem', '2rem'],
    padding: ['0rem', '1rem'],
    backgroundColor: ['#911a1a', '#243d00'],
    easing: 'easeOutExpo',
    duration: 500
  })
  .add({
    targets: '.winning-text',
    backgroundColor: [
      {value: '#fff'},
      {value: '#7a911a'}
    ],
    duration: 250,
    easing: 'easeInOutSine'
  })
};

// animates  appearance of 'blobs' inside of a music genres container
export function animateBlob() {
  const blobs = document.querySelectorAll('.blob');
  blobs.forEach(blob => {
    anime({
    targets: blob,
    opacity: [0, 1],
    scale: [3, 1],
    translateX: Math.floor(Math.random() * Math.floor(200)) - 150,
    translateY: Math.floor(Math.random() * Math.floor(200)) - 150,
    delay: anime.stagger(100)
  });
  })
}

// morphs blobs
export function animateMorphBlob() {
  const a_blob = new Blob();
  anime({
    targets: '.blob',
    opacity: [0, 1],
    scale: [1.5],
    translateX: Math.floor(Math.random() * Math.floor(200)) - 200,
    translateY: Math.floor(Math.random() * Math.floor(200)) - 200,
    delay: anime.stagger(100)
  });
    const paths = document.querySelectorAll('.blob path');
    paths.forEach(path => {
      anime({
        targets: path,
        d: a_blob.getMorphed(),
        fill: a_blob.getColored(),
        easing: 'easeOutElastic(4, 0.5)',
        delay: anime.stagger(100),
        duration: 1500
      });
    });
};

// animates vinyl blocks, circles inside of them, and text on About page
export function animateAboutItems() {
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
  anime({
    targets: ".center-circle",
    scale: [0, 1],
    translateX: ['0%', '-50%'],
    translateY: ['-50%'],
    delay: anime.stagger(60, {easing: 'easeOutQuad'})
  })
};

// animates bottom frame play buttons (e.g. save collage, guess albums, guess artists)
export function animatePlayButtons(elementsList, delay) {
 anime({
   targets: elementsList,
   opacity: [0, 1],
   scale: [0.8, 1],
   duration: 600,
   delay: 110 * delay,
   easing: 'easeOutExpo'
 })
}

// animates user's avatar
export function animateAvatar(delay) {
  const avatarjke = document.querySelector('.avatar-container');
  console.log(avatarjke);
  console.log('animating avatar')
  let tl = anime.timeline({
    easing: 'easeOutExpo',
    duration: 350
  });
  tl
  .add({
    targets: '.avatar-container',
    scale: [0.5, 1],
    translateY: [50, 0],
    opacity: [0, 1],
    borderRadius: ['200px', '0px'],
    delay: 90 * delay
  })
  .add({
    targets: ".username",
    backgroundColor: ["#FFF", "#005191"],
    scale: [2, 1],
    opacity: [0.5, 1],
  })
}

export function animateNavigationBar() {
  anime({
    targets: '.method',
    translateX: [
      {value: "50%", easing: 'easeOutQuad', duration: 50},
      {value: "0%", easing: 'easeOutQuad', duration: 50}
    ],
    opacity: [0, 1],
    delay: anime.stagger(110, {easing: 'easeOutQuad'}),
  });
};


export function animateSpotifyWidget() {
  anime({
    targets: '.widget-wrapper',
    translateY: [
      {value: "50%", easing: 'easeOutQuad', duration: 50},
      {value: "0%", easing: 'easeOutQuad', duration: 50}
    ],
    opacity: [0, 1]
  });

}