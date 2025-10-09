from utils.database_connection import get_collection

def update_harimanga_mangaurl():
    # Target collections
    collections_to_update = [
        "get_manga_links",
        "get_manga_chapters",
        "get_manga_details",
        "get_csv_links",
    ]

    # Domain change
    old_domain = "harimanga.com"
    new_domain = "harimanga.me"

    for coll_name in collections_to_update:
        collection = get_collection(coll_name)

        # Update all documents where manga_url contains the old domain
        result = collection.update_many(
            {"Manga_url": {"$regex": old_domain}},
            [
                {
                    "$set": {
                        "Manga_url": {
                            "$replaceOne": {
                                "input": "$Manga_url",
                                "find": old_domain,
                                "replacement": new_domain,
                            }
                        }
                    }
                }
            ],
        )

        print(f"✅ [{coll_name}] Updated {result.modified_count} documents.")

if __name__ == "__main__":
    update_harimanga_mangaurl()
