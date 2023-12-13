from flask import Flask, jsonify
from utils.database_connection import get_collection

app = Flask(__name__)

links_collection = get_collection("get_manga_links")


@app.route("/")
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


if __name__ == "__main__":
    app.run(debug=True)
