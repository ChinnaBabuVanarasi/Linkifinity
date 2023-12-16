import re
import pandas as pd

try:
    from utils.common_functions import delete_collection_records
    from utils.database_connection import get_collection
except ModuleNotFoundError:
    from common_functions import delete_collection_records
    from database_connection import get_collection

import pandas as pd
from urllib.parse import urlparse


def insert_links_from_csv(filepath, collection):
    df = pd.read_csv(filepath)

    bulk_operations = []
    for i, row in df.iterrows():
        link = row["links"]
        path_segments = link.split("/")

        # Extract title and site
        title_var = re.sub(r"[^a-zA-z0-9]", " ", path_segments[-2])
        title_var = title_var.replace("01", "") if title_var[-2:] == "01" else title_var

        title = " ".join(
            [
                word.capitalize() if len(word) > 1 else word
                for word in title_var.split(" ")
            ]
        )

        site = path_segments[2]

        data = {"Title": title, "Site": site, "Manga_url": link}
        # Check existence of the title in the collection
        existing_doc = collection.find_one({"Title": title})
        if not existing_doc:
            bulk_operations.append(data)
            print(f"Inserted: {i}, {link}")
        else:
            print(f"Not Inserted: {link}, {title}")

    if bulk_operations:
        collection.insert_many(bulk_operations)


collection_name = get_collection("get_manga_links")
fileinput = (
    "/media/charan/code/Myprojects/PythonProjects/Linkifinity/csvfiles/links.csv"
)
insert_links_from_csv(fileinput, collection=collection_name)
# delete_collection_records(collection_name)
