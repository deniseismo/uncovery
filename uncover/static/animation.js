import anime from './anime.es.js'
import {Wave, Blob} from './shapes.js'

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

export function animateWaves(method) {
  const theWave = new Wave(method);

  anime({
    targets: '#wave-path-3',
    d: [
      {
        value: theWave.getWave()['d'],
        duration: 300,
        easing: 'easeInOutBack'
      }
    ],
    fill: theWave.getWave()['fill']
  });
};

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

export function animateMusicGenreOn(musicGenreElement) {
  anime({
    targets: musicGenreElement,
    scale: [0.8, 1],
    translateY: [50, 0],
    opacity: [0, 1],
    duration: 500
  });
};

export function animateBlockOff(block) {
  console.log(`animating! ${block}`)
  anime({
    targets: `#${block}`,
    scale: [1, 0],
    translateY: [0, 50],
    opacity: [1, 0],
    duration: 500,
    backgroundColor: "#ed6663"
  });
};

export function animateHighlightGuessedAlbum(album) {
  anime({
    targets: album,
    opacity: [
      {value: 0.3, easing: 'easeOutElastic(5, 0.3)', duration: 200},
      {value: 1, easing: 'easeOutElastic(5, 0.3)', duration: 400}
    ]
  });
};

export function animateMusicGenresContainer() {
  anime({
    targets: '.music-genres-container',
    scale: [0.5, 1],
    translateY: [50, 0],
    opacity: [0, 1],
    borderRadius: ['200px', '0px'],
    duration: 700
  });
}

export function animateWinningMessage() {
  anime({
    targets: '.winning-text',
    opacity: [
      {value: 0, easing: 'easeOutExpo'},
      {value: 1, easing: 'easeOutExpo'},
      {value: 0, easing: 'easeOutElastic(5, 0.3)'},
      {value: 1, easing: 'linear'}
    ],
    scale: [
      {value: 1.5, easing: 'easeOutExpo'},
      {value: 2, delay: 500},
      {value: 1, duration: 500}
    ],
    fontSize: ['0.1rem', '2rem'],
    padding: ['0rem', '1rem'],
//    borderRadius: ['50% 0% 50% 0%', '0%'],
    backgroundColor: ['#911a1a', '#243d00'],
    easing: 'easeOutExpo',
    duration: 500
  })
};

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

