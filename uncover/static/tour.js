import Shepherd from './shepherd/shepherd.esm.js';
import {cookieStorage} from './cookieconsent.js'


const noteIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Musical Note</title><path d="M240 343.31V424a32.28 32.28 0 01-21.88 30.65l-21.47 7.23c-25.9 8.71-52.65-10.75-52.65-38.32h0A34.29 34.29 0 01167.25 391l50.87-17.12A32.29 32.29 0 00240 343.24V92a16.13 16.13 0 0112.06-15.66L360.49 48.2A6 6 0 01368 54v57.76a16.13 16.13 0 01-12.12 15.67l-91.64 23.13A32.25 32.25 0 00240 181.91v39.39" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/></svg>`;
const logInIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Log In</title><path d="M192 176v-40a40 40 0 0140-40h160a40 40 0 0140 40v240a40 40 0 01-40 40H240c-22.09 0-48-17.91-48-40v-40" fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32"/><path fill="none" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="32" d="M288 336l80-80-80-80M80 256h272"/></svg>`;
const exploreIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Color Filter</title><circle cx="256" cy="184" r="120" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><circle cx="344" cy="328" r="120" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/><circle cx="168" cy="328" r="120" fill="none" stroke="currentColor" stroke-linejoin="round" stroke-width="32"/></svg>`;
const lastfmIcon = `<svg class="tour-icon" version="1.1" id="Capa_1" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" x="0px" y="0px" viewBox="0 0 512 512" style="enable-background:new 0 0 512 512;" xml:space="preserve">
<g>
	<g>
		<path d="M433.024,227.296c-4.512-1.504-8.864-2.944-13.024-4.32c-31.872-10.4-51.072-16.704-51.072-42.464    c0-20.896,15.52-36.032,36.896-36.032c16.384,0,28.608,7.072,39.552,23.008c1.024,1.472,2.976,2.016,4.544,1.152l32.16-17.056    c0.864-0.448,1.536-1.248,1.792-2.24c0.256-0.992,0.16-2.016-0.288-2.912c-17.248-31.808-42.08-47.264-75.968-47.264    c-51.552,0-84.896,32.416-84.896,82.56c0,51.264,32.256,72.032,91.712,92.352c34.432,11.936,49.696,18.24,49.696,43.712    c0,28.64-24.864,49.216-58.784,48c-35.552-1.248-46.304-20.8-59.84-52.864c-22.912-54.304-48.992-117.664-49.216-118.272    C270.144,131.936,218.272,96,153.984,96C69.088,96,0,167.776,0,256.032C0,344.224,69.088,416,153.984,416    c46.304,0,89.728-21.312,119.104-58.528c0.832-1.088,1.056-2.56,0.512-3.84l-19.392-46.528c-0.544-1.28-1.792-2.176-3.168-2.24    c-1.408-0.064-2.656,0.736-3.296,1.984c-18.336,36.384-54.272,58.976-93.76,58.976C95.712,365.824,48.32,316.576,48.32,256    s47.392-109.824,105.664-109.824c42.432,0,81.28,26.144,96.736,65.184l48.032,113.76l5.536,12.768    c21.696,52.512,53.6,76.064,103.552,76.256c59.392,0,104.16-40.896,104.16-95.104C512,264.672,483.04,244.256,433.024,227.296z"/>
	</g>
</g>
</svg>`

const spotifyIcon = `<svg class='tour-icon' enable-background="new 0 0 24 24"  viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path d="m12 24c6.624 0 12-5.376 12-12s-5.376-12-12-12-12 5.376-12 12 5.376 12 12 12zm4.872-6.344v.001c-.807 0-3.356-2.828-10.52-1.36-.189.049-.436.126-.576.126-.915 0-1.09-1.369-.106-1.578 3.963-.875 8.013-.798 11.467 1.268.824.526.474 1.543-.265 1.543zm1.303-3.173c-.113-.03-.08.069-.597-.203-3.025-1.79-7.533-2.512-11.545-1.423-.232.063-.358.126-.576.126-1.071 0-1.355-1.611-.188-1.94 4.716-1.325 9.775-.552 13.297 1.543.392.232.547.533.547.953-.005.522-.411.944-.938.944zm-13.627-7.485c4.523-1.324 11.368-.906 15.624 1.578 1.091.629.662 2.22-.498 2.22l-.001-.001c-.252 0-.407-.063-.625-.189-3.443-2.056-9.604-2.549-13.59-1.436-.175.048-.393.125-.625.125-.639 0-1.127-.499-1.127-1.142 0-.657.407-1.029.842-1.155z"/></svg>`
const smileyFaceIcon = `<svg xmlns="http://www.w3.org/2000/svg" class="tour-icon" viewBox="0 0 512 512"><title>Happy</title><circle cx="184" cy="232" r="24"/><path d="M256.05 384c-45.42 0-83.62-29.53-95.71-69.83a8 8 0 017.82-10.17h175.69a8 8 0 017.82 10.17c-11.99 40.3-50.2 69.83-95.62 69.83z"/><circle cx="328" cy="232" r="24"/><circle cx="256" cy="256" r="208" fill="none" stroke="currentColor" stroke-miterlimit="10" stroke-width="32"/></svg>`;


export const tour = new Shepherd.Tour({
  defaultStepOptions: {
    cancelIcon: {
      enabled: true
    },
    classes: 'class-1 class-2',
    scrollTo: { behavior: 'smooth', block: 'center' }
  }
});

tour.addStep({
  title: `explore`,
  text: `${exploreIcon}
Dive into exploration by picking your favorite <span class='italic'>genres</span> or <span class='italic'>era of music.</span>
Find your next favorite album by its cover art.`,
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
Are you into <span class='italic'>Arcade Fire</span> or <span class='italic'>Kendrick Lamar?</span> Or are you <span class='italic'>dancer?</span> Here is the place where you'll find their studio albums. Clean cover arts. No duplicates (we'd hope).`,
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
  text: `${smileyFaceIcon}Chances are you're probably using Spotify. So why not log in with it to boost your experience? Albums <span class='italic'>uncovered</span> become <span class='italic'>spotifyable.</span>`,
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

// display cookie consent message if the user's hasn't pressed 'accept' yet
export function handleWelcomeTour() {

    const tourShown = () => {
        // store it in a cookie storage
        saveToStorage(storageType);
    }
    if (shouldShowPopup(storageType)) {
        // show only if not shown before
        setTimeout(() => {
            tour.start();
        }, 2000);
        // make sure it's only shown the first time
        tourShown();
    }
};

