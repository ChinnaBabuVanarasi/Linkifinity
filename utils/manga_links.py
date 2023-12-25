from datetime import datetime
import re
from colorama import Fore
import pandas as pd


try:
    from utils.common_functions import (
        delete_collection_records,
        get_page_source,
        setup_logging,
    )
    from utils.database_connection import get_collection
except ModuleNotFoundError:
    from common_functions import (
        delete_collection_records,
        get_page_source,
        setup_logging,
    )
    from database_connection import get_collection


def get_links_from_csv(filepath):
    df = pd.read_csv(filepath)
    links = []
    for i, row in df.iterrows():
        link = row["links"]
        current_datetime = datetime.now()
        date_added = datetime(
            current_datetime.year, current_datetime.month, current_datetime.day
        )
        links.append({"Manga_url": link, "Date_added": date_added})
    return links


def get_links_from_db():
    csv_collection = get_collection("get_csv_links")
    records = list(csv_collection.find({}, {"_id": False}))
    return records


def insert_links_to_db(filepath="", collection="", choice=0):
    if choice == 1:
        links = get_links_from_csv(filepath)
    else:
        links = get_links_from_db()
    bulk_operations = []
    logs = []
    for i, row in enumerate(links):
        link = row["Manga_url"]
        soup = get_page_source(link)
        title = soup.find("div", class_="post-title").find("h1").text.strip()
        site = link.split("/")[2]

        data = {"Title": title, "Site": site, "Manga_url": link}
        # Check existence of the title in the collection
        existing_doc = collection.find_one(
            {"$and": [{"Title": title}, {"Manga_url": link}]}
        )
        if not existing_doc:
            data["Date_added"] = row["Date_added"]
            bulk_operations.append(data)
            print(Fore.RED, f"Inserted: {i}, {link}")
            logs.append(f"Inserted Manga: {link}")
        else:
            print(Fore.GREEN, f"{link} : {title} Already exists.")

    if bulk_operations:
        collection.insert_many(bulk_operations)
    if logs:
        logger = setup_logging(filename="manga_links_insert")
        for log in logs:
            logger.info(log)


collection_name = get_collection("get_manga_links")
# ! choice == '1' if reading links from csv files else choice == '0' if reading links from static list
fileinput = (
    "/media/charan/code/Myprojects/PythonProjects/Linkifinity/csvfiles/links.csv"
)
insert_links_to_db(filepath=fileinput, collection=collection_name)
# delete_collection_records(collection_name)
