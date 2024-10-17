import os
from pathlib import Path
from database_connection import get_collection


def find_and_delete_by_url(collection_name):
    """Finds a record by URL, presents it, and then deletes it."""
    collection = get_collection(collection_name)
    urls = get_records_in_col(collection_name)
    for url in urls:
        if url == "https://kunmanga.com/manga/children-of-the-rune/":
            print(url)
            # Delete the record
            result = collection.delete_one({"Manga_url": url})
            if result.deleted_count == 1:
                print("Record deleted successfully")
            else:
                print("Error deleting record")
        else:
            print("Record not found")


def delete_one_by_url(collection_name, urls):
    """Finds a record by URL, presents it, and then deletes it."""
    collection = get_collection(collection_name)
    for url in urls:
        # url = "https://kunmanga.com/manga/children-of-the-rune/"
        # Delete the record
        result = collection.delete_one({"Manga_url": url})
        if result.deleted_count == 1:
            print("Record deleted successfully")
        else:
            print("Error deleting record")


def get_records_in_col(collection_name):
    collection = get_collection(collection_name)
    records = [record['Manga_url'] for record in list(collection.find({}))]
    return records


def delete_all(collection_name):
    collection = get_collection(collection_name)
    result = collection.delete_many({})
    if result:
        print(f"{result.deleted_count} Records deleted successfully")
    else:
        print("Error deleting record")


chapters_col = 'get_manga_chapters'
metadata_col = 'get_manga_details'
manga_links_col = "get_manga_links"
links_col = 'get_csv_links'
urls = ['https://kunmanga.com/manga/pupillary-master/', 'https://kunmanga.com/manga/the-ghostly-doctor/',
        'https://harimanga.com/manga/voidman/', 'https://harimanga.com/manga/i-became-the-head-of-the-family/',
        'https://harimanga.com/manga/shadows-resurgence/']
# find_and_delete_by_url(collection_name=chapters_col)
delete_one_by_url(collection_name=manga_links_col, urls=urls)
# delete_all(chapters_col)
