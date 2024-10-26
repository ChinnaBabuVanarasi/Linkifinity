import os
from datetime import datetime
from pathlib import Path

import pandas as pd
from colorama import Fore

try:
    from utils.common_functions import (
        delete_collection_records,
        setup_logging,
    )
    from utils.database_connection import get_collection
except ModuleNotFoundError:
    from common_functions import (
        delete_collection_records,
        setup_logging,
    )
    from database_connection import get_collection


def get_links_from_csv(filepath):
    df = pd.read_csv(filepath)
    urls = []
    for i, row in df.iterrows():
        link = row["links"]
        urls.append(link)
    return urls


def insert_links_to_csv(links_list, collection):
    bulk_operations = []
    logs = []
    for i, link in enumerate(links_list):
        data = {"Manga_url": link}
        # Check existence of the title in the collection
        existing_doc = collection.find_one(data)
        if not existing_doc:
            current_datetime = datetime.now()
            date_added = datetime(
                current_datetime.year, current_datetime.month, current_datetime.day
            )
            data["Date_added"] = date_added
            bulk_operations.append(data)
            print(Fore.RED, f"Inserted: {i}, {link}")
            logs.append(f"Inserted Manga_link: {link}")
        else:
            print(
                Fore.GREEN, f"Manga with {Fore.RED}{link} {Fore.GREEN}Already exists."
            )

    if bulk_operations:
        collection.insert_many(bulk_operations)
    if logs:
        logger = setup_logging(filename="manga_csv_links_insert")
        for log in logs:
            logger.info(log)


def csv_links_function(choice=0):
    collection_name = get_collection("get_csv_links")
    # ! choice == '1' if reading links from csv files else choice == '0' if reading links from static list
    if choice == 1:
        fileinput = os.path.join(Path(os.getcwd()).resolve().parent, 'csvfiles/links.csv')
        links = get_links_from_csv(fileinput)
    else:
        links = ['https://manhuaus.org/manga/reincarnated-as-a-genius-prodigy-of-a-prestigious-family/',
                 'https://manhuaus.org/manga/i-created-a-salvation-organization/',
                 'https://manhuaus.org/manga/worthless-profession-dragon-tamer/'
                 ]
        insert_links_to_csv(links, collection=collection_name)


if __name__ == "__main__":
    csv_links_function(0)