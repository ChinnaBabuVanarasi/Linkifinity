import re
from flask import Flask
from database_connection import get_collection

app = Flask(__name__)

links_collection = get_collection("get_manga_links")
chapters_collection = get_collection("get_chapters")
details_collection = get_collection("get_manga_details")


# ! ############## REUSABLE DB FUNCTIONS ##############
def find_record(collection, query, projection={"_id": False}):
    record = collection.find_one(query, projection)
    if record:
        return record
    else:
        return None


def clean_SearchItem(SearchItem):
    if SearchItem.startswith("https://") and SearchItem[-1] != "/":
        SearchItem = f"{SearchItem}/"
    elif 'http://' not in SearchItem:
        SearchItem = re.sub(r"[^a-zA-Z0-9]", " ", SearchItem).capitalize()
    return SearchItem


def get_record(SearchItem, collection_name):
    SearchItem = clean_SearchItem(SearchItem)
    query = {"$or": [{"Title": SearchItem}, {"url": SearchItem}]}
    record = find_record(collection_name, query)
    if record:
        return record
    else:
        return f"No record found having title: {SearchItem}."


# TODO  -> Home Page
@app.route("/")
def home():
    return f"<h1>Welcome to Linkifinity API.</h1>"


# ?  ############# MANGALINKS API ENDPOINTS ############
# ! View All Links
@app.route("/links")
def get_all_records():
    records = list(links_collection.find({}, {"_id": False}))
    return records


# ! View Single Record(Given Url/Title)
@app.route("/links/<path:title>", methods=["GET"])
def get_record_by_title_or_url(title):
    record = get_record(title, links_collection)
    if record:
        return {"response": record}
    else:
        return {f"response: {record}"}


# ?  ############# MANGADETAILS API ENDPOINTS ###########
# ?  ############# MANGACHAPTERS API ENDPOINTS ############
# ! View All Chapters
@app.route("/chapters")
def get_all_chapters():
    records = list(chapters_collection.find({}, {"_id": False}))
    return records


# ! View Single Record(Given Url/Title)
@app.route("/chapters/<path:title>", methods=["GET"])
def get_chapter_by_title_or_url(title):
    record = get_record(title, chapters_collection)
    if record:
        return {"response": record}
    else:
        return {f"response: {record}"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
