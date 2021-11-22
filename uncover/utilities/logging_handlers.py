import csv


def log_artist_missing_from_db(artist_name: str):
    """
    logs artist's name to the csv file of all the artists not yet found in db
    :param artist_name: artist's name
    """
    try:
        with open('uncover/logging/artists_missing_from_db.csv', 'r', newline='', encoding='utf-8') as file:
            contents = file.read()
    except (IOError, OSError):
        return False
    if artist_name in contents:
        print(f"{artist_name}'s already there")
        # no need to add the artist
        return False
    with open('uncover/logging/artists_missing_from_db.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([artist_name])
        return True