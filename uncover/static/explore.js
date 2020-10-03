import {frequentElements} from "./utils.js"
import {submitInput, musicFilters} from "./main.js"


export function prepareToExplore() {
  createSliderContainer();
  createSlider();
  createMusicGenresContainer();
  frequentElements.textField.id = "tag-field";
  const formContainer = document.getElementById("submit-form");
  console.log(formContainer);
  formContainer.setAttribute("id", "tags-form");
  console.log(formContainer);
  const tagsSearchInput = document.querySelector('#tag-field');
  tagsSearchInput.oninput = handleTags;
};

export async function handleTags(e) {
  const options = {
    // isCaseSensitive: false,
    // includeScore: false,
    // shouldSort: true,
    // includeMatches: false,
    // findAllMatches: false,
    minMatchCharLength: 12,
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
  const tags_list = await fetchTags();
  const fuse = new Fuse(tags_list, options);
  const pattern = e.target.value;
  const results = fuse.search(pattern).length;
  if (results > 0) {
    console.log(fuse.search(pattern));
    const okButton = document.querySelector(".ok-btn");
    musicFilters.currentTag = fuse.search(pattern)[0]['item'];
    okButton.disabled = false;
  } else {
    const okButton = document.querySelector(".ok-btn");
    okButton.disabled = true;
  };
};

export function createMusicGenresContainer() {
  const musicGenresContainer = document.createElement('div');
  musicGenresContainer.classList.add('music-genres-container', 'shadow-main');
  const selectedFilters = document.createElement('h1');
  selectedFilters.textContent = "FILTERS SELECTED";
  const timeSpanElement = document.createElement('p');
  timeSpanElement.classList.add('time-span');
  const timeSpanSlider = document.querySelector('#time-span-slider');
  musicFilters.timeSpanInfo = timeSpanSlider.noUiSlider.get();
  timeSpanElement.textContent = `ticking away ${musicFilters.timeSpanInfo[0]}—${musicFilters.timeSpanInfo[1]}`;
  musicGenresContainer.appendChild(selectedFilters);
  musicGenresContainer.appendChild(timeSpanElement);
  document.querySelector('main').appendChild(musicGenresContainer);
  musicFilters.tagsPickedInfo.forEach(tag => {
    createMusicGenreElement(tag);
  });
};

function createMusicGenreElement(musicGenre) {
  const musicGenreElement = document.createElement('p');
  musicGenreElement.classList.add('music-genre-element', 'shadow-main');
  musicGenreElement.id = musicGenre;
  musicGenreElement.textContent = `${musicGenre}`;
  const musicGenresContainer = document.querySelector('.music-genres-container');
  musicGenresContainer.appendChild(musicGenreElement);
  document.querySelectorAll('.music-genre-element').forEach(genre => {
    genre.addEventListener('click', (e) => {
      musicFilters.removeMusicGenre(e.target.id)
      e.target.remove();
    });

  });
};

export function createSliderContainer() {
  const okButton = document.querySelector(".ok-btn");
  okButton.value = 'ADD';
  okButton.disabled = true;
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
  filterButton.value = 'uncover';
  filterButton.classList.add('btn', 'button', 'shadow-main', 'play-button', 'visible');
  filterButton.addEventListener('click', submitInput);
  sliderContainer.appendChild(sliderBar);
  sliderContainer.appendChild(filterButton);
  frequentElements.searchAndOptionsContainer.appendChild(sliderContainer);
};

/* activates/creates a Slider object (range slider) */
export function createSlider() {
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
        musicFilters.timeSpanInfo = timeSpanSlider.noUiSlider.get();
        const timeSpanElement = document.querySelector('.time-span');
        timeSpanElement.textContent = `ticking away ${musicFilters.timeSpanInfo[0]}–${musicFilters.timeSpanInfo[1]}`;
    });
};

function addMusicTags() {
  if (frequentElements.activeButtonID() === 'explore') {
    const tagsSearchInput = document.querySelector('#tag-field');
    if (musicFilters.tagsPickedInfo.length > 2) {
      console.log('too many tags to filter');
      return false;
    };
    if (!(musicFilters.tagsPickedInfo.includes(musicFilters.currentTag))) {
      musicFilters.addMusicGenre(musicFilters.currentTag);
      createMusicGenreElement(musicFilters.currentTag);
      console.log(`${musicFilters.currentTag} was successfully added to the tags.`);
      console.log(musicFilters.tagsPickedInfo);
    } else {
      console.log(`${musicFilters.currentTag} already exists.`);
      return false;
    };
  }
};

async function fetchTags() {
  const response = await fetch('get_tags');
  const tags = await response.json();
  return tags;
}