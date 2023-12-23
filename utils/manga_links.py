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


def insert_links_from_csv(filepath, collection):
    df = pd.read_csv(filepath)

    bulk_operations = []
    logs = []
    for i, row in df.iterrows():
        link = row["links"]
        soup = get_page_source(link)
        title = soup.find("div", class_="post-title").find("h1").text.strip()
        site = link.split("/")[2]

        data = {"Title": title, "Site": site, "Manga_url": link}
        # Check existence of the title in the collection
        existing_doc = collection.find_one(
            {"$and": [{"Title": title}, {"Manga_url": link}]}
        )
        if not existing_doc:
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
fileinput = (
    "/media/charan/code/Myprojects/PythonProjects/Linkifinity/csvfiles/links.csv"
)
insert_links_from_csv(fileinput, collection=collection_name)
# delete_collection_records(collection_name)
