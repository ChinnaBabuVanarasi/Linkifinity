import os
from datetime import datetime

from flask import Flask, jsonify
from flask_cors import CORS

from database_connection import get_collection

app = Flask(__name__)
CORS(app)


# ! ############## REUSABLE DB FUNCTIONS ##############
def format_date_records(records):
    for record in records:
        if "Latest_chapters" in record:
            for chapter in record["Latest_chapters"]:
                formatted_date = datetime.strftime(chapter["chapter_added"], "%d %B %Y")
                chapter["chapter_added"] = formatted_date
    return records


def find_record(collection, query, projection=None):
    if projection is None:
        projection = {"_id": False}
    record = collection.find_one(query, projection)
    if record:
        return record
    else:
        return None


def get_record(searchitem, collection_name):
    query = {"$or": [{"Title": searchitem}, {"Manga_url": searchitem}]}
    print(query, collection_name)
    record = find_record(collection_name, query)
    if record:
        return record
    else:
        return f"No record found having title: {searchitem}."


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


# ADDING MANGA LINKS API ###################################
@app.route('/add_link/<path:title>', methods=['GET'])
def add_manga_link(title):
    try:
        # Get user input from request
        # user_input = request.json['user_input']

        # Check if manga link already exists
        print('title:', title)
        csv_collection = get_collection("get_csv_links")
        existing_data = get_record(title, csv_collection)
        print('existing_data:', existing_data)
        if 'No record found having title' not in existing_data:
            message = "Data already exists in the database!"
        else:
            # Insert manga link into MongoDB collection
            current_datetime = datetime.now()
            date_added = datetime(
                current_datetime.year, current_datetime.month, current_datetime.day
            )
            data = {
                "Manga_url": title,
                "Date_added": date_added
            }
            csv_collection.insert_one(data)
            message = "Data saved successfully to MongoDB!"

        return jsonify({'message': message}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
