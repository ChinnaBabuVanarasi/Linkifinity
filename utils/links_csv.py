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


def insert_links_to_csv(links, collection):
    bulk_operations = []
    logs = []
    for i, link in enumerate(links):
        data = {"Manga_url": link}
        # Check existence of the title in the collection
        existing_doc = collection.find_one(data)
        if not existing_doc:
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
        logger = setup_logging(filename="manga_links_insert")
        for log in logs:
            logger.info(log)


collection_name = get_collection("get_csv_links")
links = ["https://kunmanga.com/manga/invincible-at-the-start/"]
insert_links_to_csv(links, collection=collection_name)
# delete_collection_records(collection_name)
