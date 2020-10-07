import anime from './anime.es.js'
import {Wave} from './wave.js'

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

export function animateMusicGenreOff(musicGenreElement) {
  anime({
    targets: `#${musicGenreElement}`,
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
