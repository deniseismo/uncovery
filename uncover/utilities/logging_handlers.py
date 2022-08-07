import csv
import os

from flask import current_app


def log_artist_missing_from_db(artist_name: str) -> bool:
    """
    log missing artists from db to the log csv file
    :param artist_name: (str) artist's name
    """
    MISSING_ARTISTS_FILENAME = "artists_missing_from_db.csv"
    MISSING_ARTISTS_PATH = os.path.join(current_app.root_path, "logging", MISSING_ARTISTS_FILENAME)
    try:
        with open(MISSING_ARTISTS_PATH, 'r', newline='', encoding='utf-8') as file:
            contents = file.read()
    except (IOError, OSError) as e:
        print(e)
        return False
    if artist_name in contents:
        # no need to add the artist
        print(f"missing Artist({artist_name}) has already been added to the missing artists list")
        return False
    with open(MISSING_ARTISTS_FILENAME, 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([artist_name])
        return True


def log_arbitrary_data(data_to_log: str, filename: str) -> bool:
    """
    :param data_to_log: any data you want to log in
    :param filename: filename to save data into
    """
    filepath = os.path.join(current_app.root_path, 'dev/logs', filename)
    try:
        with open(filepath, 'a+', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow([data_to_log])
    except IOError as e:
        print('file not found', e)
        return False
