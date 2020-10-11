import {Blob} from "./shapes.js"
import {frequentElements} from "./utils.js"
import {theGame, submitInput, musicFilters} from "./main.js"
import {animateTimeSpan, animateMusicGenreOn, animateBlockOff,
        animateMusicGenresContainer, animateMorphBlob, animateBlob} from './animation.js'

// prepares all the sliders and options for the EXPLORE mode
export async function prepareToExplore() {
  createSliderContainer();
  createSlider();
  createMusicGenresContainer();
  frequentElements.textField.id = "tag-field";
  const formContainer = document.getElementById("submit-form");
  formContainer.id = "tags-form";
  const tagsSearchInput = document.querySelector('#tag-field');
  tagsSearchInput.addEventListener('input', handleTags);
  tagsSearchInput.addEventListener('focus', autocompletjke);
};


function autocompletjke() {
  if (!(theGame.status)) {
    console.log('autocompletjke!')
    $('#tag-field').autocomplete({
    serviceUrl: '/get_tags',
    type: "GET",
    minChars: 2,
    onSelect: function () {
      const tagsSearchInput = document.querySelector('.form-field');
      tagsSearchInput.dispatchEvent(new Event('input'));
    },
    showNoSuggestionNotice: true,
      noSuggestionNotice: 'No such tag found.'
    });
  }
};


// search through tags
export async function handleTags(e) {
  console.log(e.target.value);
  const options = {
    // isCaseSensitive: false,
    // includeScore: false,
    // shouldSort: true,
    // includeMatches: false,
    // findAllMatches: false,
    minMatchCharLength: 5,
    location: 2,
    threshold: 0.015,
    // distance: 100,
    // useExtendedSearch: false,
    // ignoreLocation: false,
    // ignoreFieldNorm: false,
    keys: [
      "names",
    ]
  };
  // get current tags list
  const tags_list = await fetchTags(e.target.value);
  console.log(tags_list);
  const fuse = new Fuse(tags_list['suggestions'], options);
  const pattern = e.target.value;
  // if something was found
  const results = fuse.search(pattern).length;
  if (results > 0) {
    console.log(fuse.search(pattern));
    // makes currentTag = the tag that was actually found
    musicFilters.currentTag = fuse.search(pattern)[0]['item'];
    // activates 'add' button so you can add the tag to the list
    const okButton = document.querySelector(".ok-btn");
    okButton.disabled = false;
  } else {
    // deactivates button otherwise
    const okButton = document.querySelector(".ok-btn");
    okButton.disabled = true;
  };
};




// a container with music tags/genres filters chosen
function createMusicGenresContainer() {
  const musicGenresContainer = document.createElement('div');
  musicGenresContainer.classList.add('music-genres-container', 'shadow-main');
  const selectedFilters = document.createElement('h1');
  selectedFilters.textContent = "FILTERS APPLIED";
  const calendarIcon = document.createElement("img");
  calendarIcon.src = "/static/images/filters/calendar.png";
  calendarIcon.classList.add("calendarIcon");
  const timeSpanElement = document.createElement('p');
  timeSpanElement.classList.add('time-span');
  const timeSpanBegin = document.createElement('span');
  timeSpanBegin.classList.add('time-span-begin');
  const timeSpanEnd = document.createElement('span');
  timeSpanEnd.classList.add('time-span-end');
  const timeSpanDelimit = document.createElement('span');
  timeSpanDelimit.classList.add('time-span-delimit');
  timeSpanElement.appendChild(timeSpanBegin);
  timeSpanElement.appendChild(timeSpanDelimit);
  timeSpanElement.appendChild(timeSpanEnd);
  const timeSpanSlider = document.querySelector('#time-span-slider');
  // get current/default time span values
  musicFilters.timeSpanInfo = timeSpanSlider.noUiSlider.get();
  // display the current time span
  timeSpanBegin.textContent = musicFilters.timeSpanInfo[0];
  timeSpanDelimit.textContent = "—";
  timeSpanEnd.textContent = musicFilters.timeSpanInfo[1];
  addBlob(musicGenresContainer, 3);
  musicGenresContainer.appendChild(selectedFilters);
  musicGenresContainer.appendChild(timeSpanElement);
  document.querySelector('main').appendChild(musicGenresContainer);
  animateBlob();
  animateMusicGenresContainer(musicGenresContainer);
  // display all the tags already chosen/left from before
  musicFilters.tagsPickedInfo.forEach(tag => {
    createMusicGenreElement(tag);
  });
};

function createMusicGenreElement(musicGenre) {
  const musicGenreElement = document.createElement('p');
  musicGenreElement.classList.add('music-genre-element', 'shadow-main');
  musicGenreElement.id = `tag-${musicGenre.replace(/\s/g, '')}`;
  musicGenreElement.dataset.tagName = musicGenre;
  musicGenreElement.textContent = `${musicGenre}`;
  const musicGenresContainer = document.querySelector('.music-genres-container');
  musicGenresContainer.appendChild(musicGenreElement);
  animateMusicGenreOn(musicGenreElement);
  document.querySelectorAll('.music-genre-element').forEach(genre => {
    genre.addEventListener('click', (e) => {
      musicFilters.removeMusicGenre(e.target.dataset.tagName);
      animateBlockOff(e.target.id);
      animateMorphBlob();
      setTimeout(() => {
        e.target.remove();
      }, 100);
    });
  });
};


function addBlob(parentElement, numberOfBlobs) {
  const a_blob = new Blob();
  for (let i = 0; i < numberOfBlobs; i++) {
    const blob_element = a_blob.getBlob();
    parentElement.appendChild(blob_element);
  }
};





// creates a timespan slider container
function createSliderContainer() {
  // make an 'ok' button the 'add' button
  const okButton = document.querySelector(".ok-btn");
  okButton.value = 'ADD';
  okButton.disabled = true;
  // add listener to the button
  okButton.addEventListener('click', addMusicTags);

  const sliderContainer = document.createElement("div");
  sliderContainer.classList.add('slider-container');
  const sliderBar = document.createElement("div");
  sliderBar.classList.add('slider-bar');
  const slider = document.createElement("div");
  slider.id = "time-span-slider";
  sliderBar.appendChild(slider);
  const filterButton = document.createElement('input');
  filterButton.id = 'submit-filter';
  filterButton.type = 'submit';
  filterButton.value = 'UNCOVER';
  filterButton.classList.add('btn', 'button', 'shadow-main', 'play-button', 'visible');
  filterButton.addEventListener('click', submitInput);
  sliderContainer.appendChild(sliderBar);
  sliderContainer.appendChild(filterButton);
  frequentElements.searchAndOptionsContainer.appendChild(sliderContainer);
};

/* activates/creates a Slider object (range slider) */
function createSlider() {
    const timeSpanSlider = document.getElementById('time-span-slider');
    noUiSlider.create(timeSpanSlider, {
        start: [musicFilters.timeSpanInfo[0], musicFilters.timeSpanInfo[1]],
        tooltips: true,
        connect: true,
        padding: 0,
        step: 1,
        range: {
            'min': 1950,
            'max': 2020
        },
        pips: {
            mode: 'values',
            values: [1965, 1985, 2010],
            density: 10
        },
        format: {
            to: function (value) {
                return parseInt(value);
            },
            from: function (value) {
                return parseInt(value);
            }
        }
    });

    timeSpanSlider.noUiSlider.on('change', (values, handle) => {
        const timeBefore = musicFilters.timeSpanInfo;
        musicFilters.timeSpanInfo = timeSpanSlider.noUiSlider.get();
        const timeAfter = musicFilters.timeSpanInfo;
        const timeSpanElement = document.querySelector('.time-span');
        animateTimeSpan(timeBefore, timeAfter);
//        timeSpanElement.textContent = `ticking away ${musicFilters.timeSpanInfo[0]}–${musicFilters.timeSpanInfo[1]}`;
    });
};




function addMusicTags() {
  // add current chosen music tag to the list
  if (frequentElements.activeButtonID() === 'explore') {
    if (musicFilters.tagsPickedInfo.length > 2) {
      // tags limit is set to 3, => can't add anymore
      console.log('too many tags to filter');
      return false;
    };
    // checks if the tag's already been added
    if (!(musicFilters.tagsPickedInfo.includes(musicFilters.currentTag))) {
      // add tag to the list of chosen filters
      musicFilters.addMusicGenre(musicFilters.currentTag);
      // creates a DOM element with the tag
      createMusicGenreElement(musicFilters.currentTag);
      animateMorphBlob();
      console.log(`${musicFilters.currentTag} was successfully added to the tags.`);
      console.log(musicFilters.tagsPickedInfo);
    } else {
      console.log(`${musicFilters.currentTag} already exists.`);
      return false;
    };
  }
};

async function fetchTags(value) {
  // fetches current tags list
  const response = await fetch('get_tags', {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({"query": value})
  });
  const tags = await response.json();
  return tags;
};

export function cleanAfterExplore() {
  const sliderContainer = document.querySelector('.slider-container');
  const musicGenresContainer = document.querySelector('.music-genres-container');
  [sliderContainer, musicGenresContainer].forEach(container => {
    if (container) {
      container.remove();
    };
  });
  const okButton = document.querySelector(".ok-btn");
  okButton.value = 'OK';
  okButton.disabled = false;
  const formField = document.querySelector('.form-field');
  formField.id = "text-field";
  formField.removeEventListener("input", handleTags);
  $('.form-field').autocomplete('dispose');
};