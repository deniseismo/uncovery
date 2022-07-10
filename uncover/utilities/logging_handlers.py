import csv
import os

from flask import current_app


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


def log_arbitrary_data(data_to_log: str, filename: str):
    """
    :param data_to_log: any data you want to log in
    :param filename: filename to save data into
    :return:
    """
    filepath = os.path.join(current_app.root_path, 'dev/logs', filename)
    try:
        with open(filepath, 'a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([data_to_log])
    except IOError as e:
        print('file not found', e)
        return None
