import Shepherd from './shepherd/shepherd.esm.js';
import {cookieStorage} from './cookieconsent.js'


const noteIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Musical Note</title><path d="M240 343.31V424a32.28 32.28 0 01-21.88 30.65l-21.47 7.23c-25.9 8.71-52.65-10.75-52.65-38.32h0A34.29 34.29 0 01167.25 391l50.87-17.12A32.29 32.29 0 00240 343.24V92a16.13 16.13 0 0112.06-15.66L360.49 48.2A6 6 0 01368 54v57.76a16.13 16.13 0 01-12.12 15.67l-91.64 23.13A32.25 32.25 0 00240 181.91v39.39" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/></svg>`;
const logInIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Log In</title><path d="M192 176v-40a40 40 0 0140-40h160a40 40 0 0140 40v240a40 40 0 01-40 40H240c-22.09 0-48-17.91-48-40v-40" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M288 336l80-80-80-80M80 256h272"/></svg>`;
const exploreIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Mix and Match</title><circle cx="256" cy="184" r="120" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><circle cx="344" cy="328" r="120" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><circle cx="168" cy="328" r="120" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/></svg>`;
const lastfmIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 24 24"><title>last.fm brand</title><path d="M10.584 17.209l-.88-2.392s-1.43 1.595-3.573 1.595c-1.897 0-3.244-1.65-3.244-4.289 0-3.381 1.704-4.591 3.382-4.591 2.419 0 3.188 1.567 3.849 3.574l.88 2.75c.879 2.667 2.528 4.811 7.284 4.811 3.409 0 5.719-1.044 5.719-3.793 0-2.227-1.265-3.381-3.629-3.932l-1.76-.385c-1.209-.275-1.566-.77-1.566-1.594 0-.935.742-1.485 1.952-1.485 1.319 0 2.034.495 2.144 1.677l2.749-.33c-.22-2.474-1.924-3.491-4.729-3.491-2.474 0-4.893.935-4.893 3.931 0 1.87.907 3.052 3.188 3.602l1.869.439c1.402.33 1.869.907 1.869 1.705 0 1.017-.989 1.43-2.858 1.43-2.776 0-3.932-1.457-4.591-3.464l-.907-2.749c-1.155-3.574-2.997-4.894-6.653-4.894-4.041-.001-6.186 2.556-6.186 6.899 0 4.179 2.145 6.433 5.993 6.433 3.107.001 4.591-1.457 4.591-1.457z"/></svg>`
const spotifyIcon = `<svg xmlns="http://www.w3.org/2000/svg" class='tour-icon' viewBox="0 0 24 24"><path d="M19.098 10.638c-3.868-2.297-10.248-2.508-13.941-1.387-.593.18-1.22-.155-1.399-.748-.18-.593.154-1.22.748-1.4 4.239-1.287 11.285-1.038 15.738 1.605.533.317.708 1.005.392 1.538-.316.533-1.005.709-1.538.392zm-.126 3.403c-.272.44-.847.578-1.287.308-3.225-1.982-8.142-2.557-11.958-1.399-.494.15-1.017-.129-1.167-.623-.149-.495.13-1.016.624-1.167 4.358-1.322 9.776-.682 13.48 1.595.44.27.578.847.308 1.286zm-1.469 3.267c-.215.354-.676.465-1.028.249-2.818-1.722-6.365-2.111-10.542-1.157-.402.092-.803-.16-.895-.562-.092-.403.159-.804.562-.896 4.571-1.045 8.492-.595 11.655 1.338.353.215.464.676.248 1.028zm-5.503-17.308c-6.627 0-12 5.373-12 12 0 6.628 5.373 12 12 12 6.628 0 12-5.372 12-12 0-6.627-5.372-12-12-12z"/></svg>`

const smileyFaceIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Smiley Face</title><circle cx="184" cy="232" r="24"/><path d="M256.05 384c-45.42 0-83.62-29.53-95.71-69.83a8 8 0 017.82-10.17h175.69a8 8 0 017.82 10.17c-11.99 40.3-50.2 69.83-95.62 69.83z"/><circle cx="328" cy="232" r="24"/><circle cx="256" cy="256" r="208" fill="none" stroke="currentColor" stroke-miterlimit="10" stroke-width="32"/></svg>`;


export const tour = new Shepherd.Tour({
  defaultStepOptions: {
    cancelIcon: {
      enabled: true
    },
    classes: 'shadow-main',
    scrollTo: { behavior: 'smooth', block: 'center' }
  }
});

tour.addStep({
  title: `explore`,
  text: `${exploreIcon}
Dive into exploration by picking your favorite <span class='italic'>genres</span> or <span class='italic'>era of music.</span>
Mix and match whatever you want. Find your next favorite album by its cover art.`,
  attachTo: {
    element: '#explore',
    on: 'bottom'
  },
  buttons: [
    {
      action() {
        return this.next();
      },
      text: 'Next'
    }
  ],
  id: 'creating'
});
tour.addStep({
  title: 'Last.fm',
  text: `${lastfmIcon}
Create an awesome collage out of your Last.fm charts. Guess the albums by their cover arts, play, get ready for <span class='italic'>uncovery.</span>`,
  attachTo: {
    element: '#by_lastfm_username',
    on: 'bottom'
  },
  buttons: [
    {
      action() {
        return this.back();
      },
      classes: 'shepherd-button-secondary',
      text: 'Back'
    },
    {
      action() {
        return this.next();
      },
      text: 'Next'
    }
  ],
  id: 'creating'
});
tour.addStep({
  title: 'artist',
  text: `${noteIcon}
Are you into <span class='italic'>Arcade Fire</span> or <span class='italic'>Kendrick Lamar?</span> Search for your favorite artists and uncover their albums. Treat yourself with a good old collage! Check how well you know the discography.`,
  attachTo: {
    element: '#by_artist',
    on: 'bottom'
  },
  buttons: [
    {
      action() {
        return this.back();
      },
      classes: 'shepherd-button-secondary',
      text: 'Back'
    },
    {
      action() {
        return this.next();
      },
      text: 'Next'
    }
  ],
  id: 'creating'
});
tour.addStep({
  title: 'spotify',
  text: `${spotifyIcon}
Have fun with your top records. Might have to log in for this one!`,
  attachTo: {
    element: '#by_spotify',
    on: 'bottom'
  },
  buttons: [
    {
      action() {
        return this.back();
      },
      classes: 'shepherd-button-secondary',
      text: 'Back'
    },
    {
      action() {
        return this.next();
      },
      text: 'Next'
    }
  ],
  id: 'creating'
});
tour.addStep({
  title: 'log in',
  text: `${smileyFaceIcon}Chances are you're probably using Spotify. So why not log in with it to boost your experience? All site's features get enhanced! Albums <span class='italic'>uncovered</span> become <span class='italic'>spotifyable.</span>`,
  attachTo: {
    element: '.spotify-login-container',
    on: 'bottom'
  },
  buttons: [
    {
      action() {
        return this.back();
      },
      classes: 'shepherd-button-secondary',
      text: 'Back'
    },
    {
      action() {
        return this.next();
      },
      text: 'done'
    }
  ],
  id: 'creating'
});



const storageType = cookieStorage;
const tourName = 'uncovery_welcome_tour';
const shouldShowPopup = () => !storageType.getItem(tourName);
const saveToStorage = () => storageType.setItem(tourName, true);



export function prepareAndStartTour() {
  const mediaQuery = window.matchMedia('(min-width: 851px)')
    if (!mediaQuery.matches) {
      // change tour's 'attach' behaviour for smaller devices, make the tour appear in the middle
      tour.steps.forEach(step => {
              step.updateStepOptions({
              "attachTo": ""
              })
            })
    }
    tour.start();
}


// display cookie consent message if the user's hasn't pressed 'accept' yet
export function handleWelcomeTour() {

    const tourShown = () => {
        // store it in a cookie storage
        saveToStorage(storageType);
    }
    if (shouldShowPopup(storageType)) {
        // show only if not shown before
        setTimeout(() => {
            prepareAndStartTour();
        }, 2000);
        // make sure it's only shown the first time
        tourShown();
    } else {
       const helpTourIcon = document.querySelector('.help-tour-icon');
       helpTourIcon.classList.add('on');
       helpTourIcon.addEventListener('click', () => {
         if (!Shepherd.activeTour) {
           prepareAndStartTour();
         }
       });
    }
};

