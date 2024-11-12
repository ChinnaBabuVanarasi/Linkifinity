import base64

import pandas as pd
import requests

try:
    from common_functions import (
        get_page_source,
        setup_logging,
        delete_collection_records,
        mongodb_insertion,
    )
    from database_connection import get_collection, close_database_connection
except ModuleNotFoundError:
    from utils.common_functions import (

        get_page_source,
        setup_logging,
        delete_collection_records,
        mongodb_insertion,
    )
    from utils.database_connection import get_collection, close_database_connection

url = 'https://kunmanga.com/manga/academy-s-genius-swordmaster/chapter-73/'

soup = get_page_source(url)
images_tag = soup.find('input', {'id': 'wp-manga-current-chap'}).parent
images_list = images_tag.find_all("img", class_='wp-manga-chapter-img')
image_links = []
for img in images_list:
    image = img['src'].strip()
    image_links.append(image)

images_en_list = []
for i in range(len(image_links)):
    try:
        response = requests.get(image_links[i])

        if response.status_code == 200:
            image_data = response.content
            en_image = base64.b64encode(image_data).decode("utf-8")
        else:
            print("An error occurred:Not Able tp encode image")
            en_image = ''
        images_en_list.append({"page": i, "image": image_links[i], "binary_image": en_image})
    except Exception as e:
        print("An error occurred:", str(e))
df = pd.DataFrame(images_en_list)
df.to_csv('images_en.csv', index=False)