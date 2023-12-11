import pandas as pd

from utils.database_connection import get_collection


def delete_collection_records(collection):
    collection.delete_many({})


def insert_links_from_csv(filepath, collection):
    df = pd.read_csv(filepath)
    for i, row in df.iterrows():
        link = row["links"]
        title = link.split("/")[-2].replace("-", " ")
        if title[-2:] == '01':
            title = title.replace('01', '')
        else:
            title = title
        site = link.split("/")[2]
        data = {"Title": title, "Site": site, "url": link}
        doc = collection.find_one(data)
        if not doc:
            print(f'inserted: {i}, {link}')
            collection.insert_one(data)
        else:
            print(f'not inserted: {link}, {title}')


collection_name = get_collection("get_manga_links")
fileinput = "/media/charan/code/Myprojects/PythonProjects/Linkifinity/csvfiles/links.csv"
insert_links_from_csv(fileinput, collection=collection_name)
# delete_collection_records(collection_name)
