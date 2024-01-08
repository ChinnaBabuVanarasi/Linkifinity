import json
import os
from pathlib import Path

from pymongo import MongoClient

cached_credentials = None

global client

COLLECTIONS = {
    "get_manga_links": "MANGALINKS",
    "get_manga_images": "MANGAIMAGES",
    "get_manga_chapters": "CHAPTERSDB",
    "get_manga_details": "MANGADETAILS",
    "get_csv_links": "CSVLINKS"
}


def read_credentials():
    if not hasattr(read_credentials, "cached_credentials"):
        credentials_path = os.path.join(Path(os.getcwd()).resolve().parent, 'env/creds.json')
        # credentials_path = os.path.join(
        #     os.path.dirname(__file__), "..", "env", "creds.json"
        # )
        with open(credentials_path, "r") as f:
            read_credentials.cached_credentials = json.load(f)
    return read_credentials.cached_credentials


def create_database_connection():
    global client
    try:
        credentials = read_credentials()
        password = credentials.get("PASSWORD")
        username = credentials.get("CLUSTER")
        dbname = credentials.get("DATABASE")

        uri = f"mongodb+srv://mongodb:{password}@{username}.gwrvbi6.mongodb.net/?retryWrites=true&w=majority"
        client = MongoClient(uri)
        return client[dbname]
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        return None


def close_database_connection():
    global client
    try:
        if client:
            client.close()
            print("Closed MongoDB connection")
    except Exception as e:
        print("Error closing MongoDB connection:", e)


def get_collection(collection_name: str):
    credentials = read_credentials()
    db_connection = create_database_connection()
    collection = COLLECTIONS.get(collection_name)
    db_collection = credentials.get(collection)
    if not db_collection:
        return f"""No Collection Found with the name '{collection_name}'. 
                    Please check your collection name and try again."""
    return db_connection[db_collection]
