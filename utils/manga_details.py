import base64
import time
from colorama import Fore
import requests

try:
    from common_functions import (
        get_page_source,
        setup_logging,
        delete_collection_records,
    )
    from database_connection import get_collection
except ModuleNotFoundError:
    from utils.common_functions import (
        get_page_source,
        setup_logging,
        delete_collection_records,
    )
    from utils.database_connection import get_collection

IMAGE_CONSTANT = "/9j/4QVfRXhpZgAASUkqAAgAAAAMAAABAwABAAAALAEAAAEBAwABAAAAwgEAAAIBAwADAAAAngAAAAYBAwABAAAAAgAAABIBAwAB"


def update_no_image_records(en_image, title):
    images_collection = get_collection("get_manga_images")
    if en_image[:100] == IMAGE_CONSTANT:
        print(title)
        doc = images_collection.find_one({"Title": title})
        if doc:
            return doc["Image"]
        else:
            return en_image
    else:
        return en_image


def get_image(soup, title):
    # soup = get_page_source(url)
    tab_summary = soup.find("div", class_="tab-summary")
    image_link = tab_summary.find("a")
    image_srcset = image_link.find("img", {"srcset": True})
    image_data = image_link.find("img", {"data-src": True}) or image_link.find(
        "img", {"src": True}
    )
    if image_srcset:
        image_src = image_srcset.get("srcset").split(",")[0]
    else:
        image_src = image_data.get("data-src") or image_data.get("src")
    image_url = image_src if " " not in image_src else image_src.split(" ")[0]

    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            image_data = response.content
            en_image = base64.b64encode(image_data).decode("utf-8")
        else:
            placeholder_image_url = "/media/charan/code/Myprojects/PythonProjects/Linkifinity/placeholder.jpg"
            with open(placeholder_image_url, "rb") as f:
                image_data = f.read()
            en_image = base64.b64encode(image_data).decode("utf-8")

        b_image = update_no_image_records(en_image, title)

        return {"image": image_url, "binary_image": b_image}
    except Exception as e:
        print("An error occurred:", str(e))


def extract_meta_data(url,date_added):
    soup = get_page_source(url)
    title = soup.find("div", class_="post-title").find("h1").text.strip()
    Image_data = get_image(soup, title)
    details = {
        "Title": title,
        "Image": Image_data["image"],
        "Binary_Image": Image_data["binary_image"],
        "Manga_url": url,
        "Date_added":date_added
    }
    return details


def get_record(collection_name, query, projection={"_id": False}):
    collection = get_collection(collection_name)
    return collection.find_one(query, projection)


def extract_details_from_urls():
    urls = read_urls_from_db()
    manga_details = []
    for i, record in enumerate(urls):
        try:
            url = record["Manga_url"]
            date_added = record["Date_added"]
            url_record = get_record("get_manga_details", {"Manga_url": url})
            if not url_record:
                print(Fore.RED, i, ": ", url)
                manga_details.append(extract_meta_data(url, date_added))
                time.sleep(1)
            else:
                print(Fore.GREEN, f"{i}: {url} is already present in the database.")
        except Exception as e:
            print(Fore.MAGENTA,f"Error occurred while extracting details for {url}: {str(e)}")
    return manga_details


def read_urls_from_db():
    try:
        manga_links_collection = get_collection("get_manga_links")
        urls = list(manga_links_collection.find({}))
        # for testing
        # urls = ["https://kunmanga.com/manga/the-beast-tamed-by-the-evil-woman/"]
        return urls
    except Exception as e:
        print(f"Error occurred while reading URLs from the database: {str(e)}")
        return []


def insert_data(details_collection):
    manga_details = extract_details_from_urls()
    logfile = "manga_meta_details"
    logger = setup_logging(filename=logfile)
    logs = []
    for manga in manga_details:
        if not details_collection.find_one(
            {"Title": manga["Title"], "Manga_url": manga["Manga_url"]}
        ):
            logs.append(f"New Manga document Inserted in MongoDB -> '{manga['Title']}'")
        details_collection.update_one(
            {
                "Title": manga["Title"],
                "Manga_url": manga["Manga_url"],
                "Date_added": manga["Date_added"],
            },
            {"$set": manga},
            upsert=True,
        )
    for log in logs:
        logger.info(log)


if __name__ == "__main__":
    details_collection = get_collection("get_manga_details")
    insert_data(details_collection)

    # collection_name = get_collection("get_manga_details")
    # delete_collection_records(collection_name)
