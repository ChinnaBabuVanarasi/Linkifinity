from flask import Flask, jsonify
from database_connection import get_collection

app = Flask(__name__)

links_collection = get_collection("get_manga_links")
chapters_collection = get_collection("get_chapters")
details_collection = get_collection("get_manga_details")


def find_record(collection, query, projection={"_id": False}):
    record = collection.find_one(query, projection)
    if record:
        return record
    else:
        return None


def insert_record(collection, data):
    collection.insert_one(data)


def delete_record(collection, filter):
    return collection.delete_one(filter)


def add_link(link):
    split_link = link.split("/")
    title = split_link[-2].replace("-", " ")
    if title[-2:] == "01":
        title = title.replace("01", "")
    else:
        title = title
    site = split_link[2]
    data = {"Title": title, "Site": site, "url": link}
    doc = find_record(links_collection, data)
    if not doc:
        insert_record(links_collection, data)
        return {"response": f"Successfully inserted link: {data}"}
    else:
        return {"response": f"Not inserted, {link} already present in mangalinks DB."}


def delete_link(title):
    query = {"$or": [{"Title": title}, {"url": title}]}
    result = delete_record(links_collection, query)
    if result.deleted_count > 0:
        return {"response": f"successfully deleted record having title: {title}."}
    else:
        return {"response": f"No record found having title: {title}."}


def get_record(value):
    query = {"$or": [{"Title": value}, {"url": value}]}
    projection = {"_id": False}
    record = find_record(links_collection, query, projection)
    if record:
        return record
    else:
        return f"No record found having title: {value}."


@app.route("/")
def home():
    return {"response": "Welcome to Manga API."}


@app.route("/links")
def get_links():
    records = [record for record in links_collection.find({}, {"_id": False})]
    return records


@app.route("/add/<path:link>", methods=["GET"])
def add_link_route(link):
    return add_link(link)


@app.route("/delete/<path:title>")
def delete_link_route(title):
    return delete_link(title)


@app.route("/link/<path:title>", methods=["GET"])
def show_record(title):
    record = get_record(title)
    if record:
        return {"response": [record]}
    else:
        return {f"response: {record}"}


@app.route("/details")
def get_details():
    details = details_collection.find({}, {"_id": False})
    details_view = []
    for detail in details:
        title = detail["Title"]
        image = detail["Image"]
        url = detail["Manga_url"]
        details_view.append({"Title": title, "Image": image, "Manga_url": url})

    return details_view


@app.route("/chapter_details")
def chapter_details():
    chapter_details = chapters_collection.find({}, {"_id": False})
    details_view = []
    for detail in chapter_details:
        title = detail["Title"]
        image = detail["Image"]
        url = detail["Manga_url"]
        chapters = detail["Latest_chapters"]
        Latest_chapters = chapters if len(chapters) <= 2 else chapters[:3]
        details_view.append(
            {
                "Title": title,
                "Image": image,
                "Manga_url": url,
                "Chapters": Latest_chapters,
                "Binary_image": "Too Long to Show Here, If you want to use,Use 'Binary_Image' as key",
            }
        )

    return details_view


@app.route("/chapters")
def get_chapters():
    chapters = chapters_collection.find({}, {"_id": False})
    chapters_view = []
    for chapter in chapters:
        title = chapter["Title"]
        image = chapter["Image"]
        url = chapter["Manga_url"]
        chapters = chapter["Latest_chapters"]
        chapters_view.append(
            {
                "Title": title,
                "Image": image,
                "Manga_url": url,
                "Chapters": chapters,
                "Binary_Image": "Too Long to Show Here, If you want to use,Use 'Binary_Image' as key",
            }
        )
    return chapters_view


@app.route("/chapter/<string:title>")
def get_chapter(title):
    chapter = chapters_collection.find_one({"Title": title}, {"_id": False})
    return [chapter]


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
