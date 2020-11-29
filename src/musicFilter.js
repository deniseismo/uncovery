export class MusicFilter {
  constructor(options) {
    this.currentMusicGenre = '';
    this.tagsPicked = options.tags;
    this.timeSpan = options.timeSpan;
    this.colorsPicked = options.colors;
  };
  get currentTag() {
    return this.currentMusicGenre;
  };
  set currentTag(newGenre) {
    this.currentMusicGenre = newGenre;
  };
  addMusicGenre() {
    this.tagsPicked.push(this.currentMusicGenre);
  };
  addColor(color) {
    this.colorsPicked.push(color);
  };
  get tagsPickedInfo() {
    return this.tagsPicked;
  };
  set tagsPickedInfo(tagsList) {
    this.tagsPicked = tagsList;
  };
  get colorsPickedInfo() {
    return this.colorsPicked;
  };
  set colorsPickedInfo(colorsList) {
    this.colorsPicked = colorsList;
  };

  removeMusicGenre(musicGenre) {
    for (let i = 0; i < this.tagsPicked.length; i++) {
      if (this.tagsPicked[i] === musicGenre) {
        this.tagsPicked.splice(i, 1);
      };
    };
  };
  removeColor(color) {
    for (let i = 0; i < this.colorsPicked.length; i++) {
      if (this.colorsPicked[i] === color) {
        this.colorsPicked.splice(i, 1);
      };
    };
  };
  set timeSpanInfo(newTimeSpan) {
    this.timeSpan = newTimeSpan;
  };
  get timeSpanInfo() {
    return this.timeSpan;
  };
};

