import os
import secrets
from io import BytesIO

import requests
from PIL import Image
from flask import current_app


def save_image(image_url):
    if not image_url:
        return None
    try:
        # req = urllib.request.Request(url=image_url, headers={'User-Agent': current_app.config['APP_USER_AGENT']})
        # print(req)
        # with urllib.request.urlopen(req) as f:
        #     print(f)
        #     print("image_file", f)
        #     an_image = Image.open(urllib.request.urlopen(f)).convert('RGB')
        req = requests.get(image_url, headers={'User-Agent': current_app.config['APP_USER_AGENT']})
        an_image = Image.open(BytesIO(req.content))
        if an_image.width >= 900:
            an_image.thumbnail((900, 900), Image.ANTIALIAS)
    except Exception as e:
        print("COULD OPEN IMAGE(URL)")
        print(e)
        return None
    random_hex = secrets.token_hex(8)
    image_filename = random_hex
    image_path = os.path.join(current_app.root_path, 'static/cover_art_new_batch', image_filename)
    try:
        # save in original size
        an_image.save(f'{image_path}.jpg', quality=95)

        resized_200 = an_image
        resized_300 = an_image
        if an_image.width > 300:
            # make pictures smaller if the original is bigger than 300 pixels wide
            resized_200 = an_image.resize((200, 200), Image.LANCZOS)
            resized_300 = an_image.resize((300, 300), Image.LANCZOS)

        # save (smaller) copies
        resized_200.save(f'{image_path}-size200.jpg', quality=95)
        resized_300.save(f'{image_path}-size300.jpg', quality=95)
    except (OSError, ValueError) as e:
        print("COULD OPEN IMAGE(URL)")
        print(e)
        return None
    return image_filename
