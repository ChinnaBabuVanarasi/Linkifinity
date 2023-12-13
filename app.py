from flask import Flask, jsonify
from utils.database_connection import get_collection

app = Flask(__name__)

links_collection = get_collection("get_manga_links")
chapters_collection = get_collection("get_chapters")
details_collection = get_collection("get_manga_details")


####################### API Routes for MangaLinks DB ##############################
@app.route("/links")
def get_links():
    records = [record for record in links_collection.find({}, {"_id": False})]
    return records


@app.route("/add/<path:link>", methods=["GET"])
def add_link(link):
    title = link.split("/")[-2].replace("-", " ")
    if title[-2:] == "01":
        title = title.replace("01", "")
    else:
        title = title
    site = link.split("/")[2]
    data = {"Title": title, "Site": site, "url": link}
    doc = links_collection.find_one(data)
    if not doc:
        links_collection.insert_one(data)
        return {"response": f"Successfully inserted link: {data}"}
    else:
        return {"response": f"Not inserted, {link} already present in mangalinks DB."}


@app.route("/delete/<string:title>")
def delete_link(title):
    record = links_collection.find_one({"Title": title})
    if record:
        links_collection.delete_one(record)
        return {"response": f"successfully deleted record having title: {title}."}
    else:
        return {"response": f"No record found having title: {title}."}


@app.route("/link/<string:title>")
def show_record(title):
    record = links_collection.find_one({"Title": title}, {"_id": False})
    if record:
        return {"response": [record]}
    else:
        return {"response": f"No record found having title: {title}."}


##################################################################################


####################### API Routes for MangaDetailsDB ############################
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


######################################################################################


####################### API Routes for MangaChaptersDB ###############################


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
            {"Title": title, "Image": image, "Manga_url": url, "Chapters": chapters}
        )
    return chapters_view


@app.route("/chapter/<string:title>")
def get_chapter(title):
    chapter = chapters_collection.find_one({'Title':title}, {"_id": False})
    return [chapter]


#######################################################################################

if __name__ == "__main__":
    app.run(debug=True)
