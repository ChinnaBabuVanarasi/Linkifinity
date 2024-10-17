import pymongo
from urllib.parse import urlparse

from pymongo import collection

from utils.database_connection import get_collection


def delete_record_by_url_substring(collection, substring):
    """Deletes a MongoDB record if it contains the specified substring in a URL field."""
    # Define the filter for the query (case-insensitive search)
    collection = 'MANGAIMAGES'
    urls = [records for records in collection.find({})]
    for url in urls:
        # print(url)
        if substring in url:
            record = collection.find_one({'Manga_url': url})
            collection.delete_one(record)
            # Print the number of deleted records
            print(f"{record['Manga_url']} deleted.")


# Example Usage (Replace with your actual values)
# collection_name = get_collection("get_manga_chapters")
# url_substring = "topmanhua"

# delete_record_by_url_substring()
collection_name = get_collection("get_csv_links")
# records = [records for records in collection_name.find({}, {"Manga_url": True, "_id": False})]
# for record in records:
#     print(record['Manga_url'])
