from database_connection import get_collection


links_collection = get_collection("get_manga_links")
chapters_collection = get_collection("get_chapters")
details_collection = get_collection("get_manga_details")


links = links_collection.find({}, {"_id": False, "url": True})
chapters = chapters_collection.find({}, {"_id": False})
details = details_collection.find({}, {"_id": False})

links_unique = [link["url"] for link in links]
chapters_unique = [chapter["Manga_url"] for chapter in chapters]
details_unique = [detail["Manga_url"] for detail in details]

for link in details_unique:
    if link not in links_unique:
        print(link)

# for detail in details_unique:
#     if detail not in chapters_unique:
#         print(detail)


# To Add
# https://kunmanga.com/manga/the-max-level-player-s-100th-regression/
# the max level player s 100th regression

# To Delete
# https://manhuafast.net/manga/the-return-of-the-prodigious-swordmaster/
# https://manhuafast.net/manga/this-martial-saint-is-way-too-generous/
# https://kunmanga.com/manga/boundless-necromancer/
