from datetime import datetime
import os
import re
from flask import Flask
from database_connection import get_collection
from flask_cors import CORS

app = Flask(__name__)
CORS(app)


# ! ############## REUSABLE DB FUNCTIONS ##############
def format_date_records(records):
    for record in records:
        if "Latest_chapters" in record:
            for chapter in record["Latest_chapters"]:
                # Convert the date string to a datetime object
                date_time = datetime.strptime(
                    chapter["chapter_added"], "%a, %d %b %Y %H:%M:%S %Z"
                )
                # Format the datetime object as "dd-mm-yyyy"
                formatted_date = date_time.strftime("%d-%m-%Y")
                chapter["chapter_added"] = formatted_date
    return records


def find_record(collection, query, projection={"_id": False}):
    record = collection.find_one(query, projection)
    if record:
        return record
    else:
        return None


def get_record(SearchItem, collection_name):
    query = {"$or": [{"Title": SearchItem}, {"Manga_url": SearchItem}]}
    record = find_record(collection_name, query)
    if record:
        return record
    else:
        return f"No record found having title: {SearchItem}."


@app.route("/")
def home():
    return f"<h1>Welcome to Linkifinity API.</h1>"


# ?  ############# MANGALINKS API ENDPOINTS ############
@app.route("/links")
def get_all_records():
    links_collection = get_collection("get_manga_links")
    records = list(links_collection.find({}, {"_id": False}))
    return records


# ! View Single link data for Given Url/Title
@app.route("/links/<path:title>", methods=["GET"])
def get_record_by_title_or_url(title):
    links_collection = get_collection("get_manga_links")
    record = get_record(title, links_collection)
    return record


# ?  ############# MANGACHAPTERS API ENDPOINTS ############
# ! View All Chapters
@app.route("/chapters/")
def get_all_chapters():
    chapters_collection = get_collection("get_manga_chapters")
    records = list(chapters_collection.find({}, {"_id": False}))
    formatted_records = format_date_records(records)
    return formatted_records


# ! View Single Chapter for Given Url/Title
@app.route("/chapters/<path:title>/", methods=["GET"])
def get_chapter_by_title_or_url(title):
    chapters_collection = get_collection("get_manga_chapters")
    record = get_record(title, chapters_collection)
    if record:
        formatted_record = format_date_records([record])
        return formatted_record[0]
    else:
        return {"response": f"No record found for title: {title}"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
