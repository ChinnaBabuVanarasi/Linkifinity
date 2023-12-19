import re
from flask import Flask
from database_connection import get_collection

app = Flask(__name__)


# ! ############## REUSABLE DB FUNCTIONS ##############
def find_record(collection, query, projection={"_id": False}):
    record = collection.find_one(query, projection)
    if record:
        return record
    else:
        return None


# def clean_SearchItem(SearchValue):
#     if SearchValue.startswith("http"):
#         if SearchValue[-1] != "/":
#             SearchValue = f"{SearchValue}/"
#         else:
#             SearchValue = SearchValue
#     else:
#         SearchValue = re.sub(r"[^a-zA-Z0-9]", " ", SearchValue)
#         # SearchValue = " ".join(
#         #     [
#         #         word.capitalize() if len(word) > 3 else word
#         #         for word in SearchValue.split(" ")
#         #     ]
#         # )
#     return SearchValue


def get_record(SearchItem, collection_name):
    # title_or_url = clean_SearchItem(SearchItem)
    # print(title_or_url)
    query = {"$or": [{"Title": SearchItem}, {"Manga_url": SearchItem}]}
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
# ! View All Links data
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
    if record:
        return {"response": record}
    else:
        return {f"response: {record}"}


# # ! Delete link record data for given Url/Title
# @app.route("/links/delete/<path:title>", methods=["GET"])
# def delete_record_by_title_or_url(title):
#     links_collection = get_collection("get_manga_links")
#     record = get_record(title, links_collection)
#     if record:
#         links_collection.delete_one(record)
#         return {"response": f"Successfully deleted the {record}"}
#     else:
#         return {"response": f"No record found with the given {title}"}


# ?  ############# MANGADETAILS API ENDPOINTS ###########
# ?  ############# MANGACHAPTERS API ENDPOINTS ############
# ! View All Chapters
@app.route("/chapters/")
def get_all_chapters():
    chapters_collection = get_collection("get_manga_chapters")
    records = list(chapters_collection.find({}, {"_id": False}))
    return records


# ! View Single Chapter for Given Url/Title
@app.route("/chapters/<path:title>/", methods=["GET"])
def get_chapter_by_title_or_url(title):
    chapters_collection = get_collection("get_manga_chapters")
    record = get_record(title, chapters_collection)
    if record:
        return {"response": record}
    else:
        return {f"response: {record}"}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
