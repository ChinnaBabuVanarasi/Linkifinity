import json
import os

from pymongo import MongoClient

cached_credentials = None

global client

COLLECTIONS = {
    "get_manga_links": "MANGALINKS",
    "get_manga_images": "MANGAIMAGES",
    "get_manga_chapters": "CHAPTERSDB",
    "get_manga_details": "MANGADETAILS",
}


def read_credentials():
    """
    Reads the credentials from a JSON file and caches them for future use.

    Returns:
        dict: The credentials read from the JSON file.
    """
    if not hasattr(read_credentials, "cached_credentials"):
        credentials_path = os.path.join(
            os.path.dirname(__file__), ".", "env", "creds.json"
        )
        with open(credentials_path, "r") as f:
            read_credentials.cached_credentials = json.load(f)
    return read_credentials.cached_credentials


def create_database_connection():
    """
    Creates a connection to a MongoDB database using the provided credentials.

    Returns:
        pymongo.database.Database: The database object if the connection is successful. Otherwise, returns None.
    """
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
    """
    Retrieves a specific collection from a MongoDB database.

    Args:
        collection_name (str): The name of the collection to retrieve.

    Returns:
        collection: The collection from the database connection if found.
        str: An error message indicating that the collection was not found if not found.
    """
    credentials = read_credentials()
    db_connection = create_database_connection()
    collection = COLLECTIONS.get(collection_name)
    db_collection = credentials.get(collection)
    if not db_collection:
        return f"""No Collection Found with the name '{collection_name}'. 
                Please check your collection name and try again."""
    return db_connection[db_collection]
