export class MusicFilter {
  constructor(options) {
    this.currentMusicGenre = '';
    this.tagsPicked = options.tags;
    this.timeSpan = options.timeSpan;
  }
  get currentTag() {
    return this.currentMusicGenre;
  }
  set currentTag(newGenre) {
    this.currentMusicGenre = newGenre;
  }
  addMusicGenre() {
    this.tagsPicked.push(this.currentMusicGenre);
  }
  get tagsPickedInfo() {
    return this.tagsPicked;
  }
  set tagsPickedInfo(tagsList) {
    this.tagsPicked = tagsList;
  }

  removeMusicGenre(musicGenre) {
    for (let i = 0; i < this.tagsPicked.length; i++) {
      if (this.tagsPicked[i] === musicGenre) {
        this.tagsPicked.splice(i, 1);
      };
    };
  }
  set timeSpanInfo(newTimeSpan) {
    this.timeSpan = newTimeSpan;
  }
  get timeSpanInfo() {
    return this.timeSpan;
  }
}


