import csv

from uncover import create_app

app = create_app()
app.app_context().push()


def log_missing_info(info):
    """
    logs missing info (missing songs/albums/releases, etc.) to a file
    """
    with open('album_colors_missing_info.csv', 'a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow([info])


