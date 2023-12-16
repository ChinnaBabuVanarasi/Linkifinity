from typing import Dict, List
import re

try:
    from common_functions import (
        get_page_source,
        setup_logging,
        delete_collection_records,
        mongodb_insertion,
    )
    from database_connection import get_collection, close_database_connection
except ModuleNotFoundError:
    from utils.common_functions import (
        get_page_source,
        setup_logging,
        delete_collection_records,
        mongodb_insertion,
    )
    from utils.database_connection import get_collection, close_database_connection

logger = setup_logging(filename="chapter_details")


def get_latest_chapter(chapter):
    latest_chapter_tag = chapter.find("a").text.strip()
    latest_chapter_str = (
        latest_chapter_tag.split("-")[0]
        if "-" in latest_chapter_tag
        else latest_chapter_tag
    )
    latest_chapter_str2 = "".join(re.findall(r"\d+\.\d+|\d+", str(latest_chapter_str)))
    latest_chapter = (
        float(latest_chapter_str2)
        if "." in latest_chapter_str2
        else int(latest_chapter_str2)
    )
    return latest_chapter


def get_current_chapter(url):
    try:
        if not isinstance(url, str) or not url.startswith("http"):
            raise ValueError("Invalid URL")
        chapter_collection = get_collection("get_manga_chapters")
        doc = chapter_collection.find_one({"Manga_url": url}, {"Latest_chapters": True})
        if doc:
            return doc[0]["Latest_chapters"][0]["chapter_num"]
        return 0
    except Exception as e:
        logger.exception(f"Error occurred while interacting with the database: {e}")
        return 0


def get_chapters(manga_url, current_chapter, manga_title) -> list:
    soup = get_page_source(manga_url)

    chapters_container = soup.find("div", class_="page-content-listing.single-page")
    if chapters_container is None:
        chapters = soup.findAll("li", class_="wp-manga-chapter")
    else:
        chapters = chapters_container.findAll("li", class_="wp-manga-chapter")
    chapter_index = 0
    if current_chapter == 0:
        chapter_index = 0
    else:
        for index, chapter_element in enumerate(chapters):
            latest_chapter = get_latest_chapter(chapter_element)
            if latest_chapter == current_chapter:
                chapter_index = index
                break
            else:
                pass

    chapter_details = []
    logs = []
    for chapter_element in chapters[: chapter_index + 1]:
        latest_chapter = get_latest_chapter(chapter_element)
        if float(latest_chapter) == float(current_chapter):
            logs.append(
                f"No new chapters for '{manga_title}': {current_chapter} -> {latest_chapter}"
            )
        else:
            logs.append(
                f"New chapters for '{manga_title}': {current_chapter} -> {latest_chapter}"
            )
        chapter_url = chapter_element.find("a")["href"]
        chapter_details.append(
            {"chapter_num": latest_chapter, "chapter_url": chapter_url}
        )
    for log in logs:
        logger.info(log)
    return chapter_details


def extract_details_from_url() -> List[Dict[str, str]]:
    try:
        records = read_records_from_db()
        manga_details = []
        for i, record in enumerate(records):
            url: str = record["Manga_url"]
            if not isinstance(url, str) or not url.startswith("http"):
                print(f"Invalid URL: {url}")
                continue
            print(f"{i}: {url}")
            current_chapter = get_current_chapter(url)
            title: str = record["Title"]
            image: str = record["Image"]
            binary_image: str = record["Binary_Image"]
            if not title or not image or not binary_image:
                print(f"Missing data for record: {record}")
                continue
            chapter_details: List[Dict[str, str]] = get_chapters(
                url, current_chapter, title
            )
            details: Dict[str, str] = {
                "Title": title,
                "Image": image,
                "Binary_Image": binary_image,
                "Latest_chapters": chapter_details,
                "Manga_url": url,
            }
            manga_details.append(details)
        return manga_details
    except Exception as e:
        logger.exception(f"Error occurred in extract_details_from_url: {e}")
        return []


def read_records_from_db():
    try:
        manga_links_collection = get_collection("get_manga_details")
        urls = [record for record in manga_links_collection.find({})]
        return urls
    except Exception as e:
        print(f"Error occurred while reading URLs from the database: {str(e)}")
        return []


def insert_data(collection_var: str):
    try:
        manga_details = extract_details_from_url()
        mongodb_insertion(
            manga_details=manga_details,
            collection_var=collection_var,
            logfile="manga_details",
        )
    except Exception as e:
        logger.exception(f"Error occurred in insert_data: {e}")


if __name__ == "__main__":
    collection_name = "get_manga_chapters"
    # delete_collection_records(collection_name)
    insert_data(collection_name)
