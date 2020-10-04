export class AlbumGameInfo {
  constructor() {
    this.albumsList = [];
    this.notGuessedAlbumsList = [];
    this.guessedAlbumsCount = 0;
  };
  set albums(albums) {
    this.albumsList = albums;
  };
  get albums() {
    return this.albumsList;
  };
  set notGuessedAlbums(albums) {
    this.notGuessedAlbumsList = albums;
  };
  get notGuessedAlbums() {
    return this.notGuessedAlbumsList;
  };
  incrementAlbumsCount() {
    this.guessedAlbumsCount++;
  };
  get albumsCount() {
    return this.guessedAlbumsCount;
  }
  set albumsCount(newCount) {
    this.guessedAlbumsCount = newCount;
  }
  removeGuessedAlbum(guessedAlbumID) {
    console.log(this);

    for (let i = 0; i < this.notGuessedAlbumsList.length; i++) {
      if (this.notGuessedAlbumsList[i]['id'] === guessedAlbumID) {
        console.log(this.notGuessedAlbumsList);
        this.notGuessedAlbumsList.splice(i, 1);
        return true;
      };
    };
  };
};
