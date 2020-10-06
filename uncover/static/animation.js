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
        easing: 'easeInOutQuad'
      }
    ],
    fill: theWave.getWave()['fill']
  });
};