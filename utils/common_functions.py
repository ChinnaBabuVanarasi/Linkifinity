import logging
import os
from datetime import datetime
from colorama import Fore

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

try:
    from utils.database_connection import get_collection
except ModuleNotFoundError:
    from database_connection import get_collection


# Delete all records from a collection


def delete_collection_records(collection_name):
    # collection_name = get_collection(name)
    collection_name.delete_many({})


def setup_logging(filename):
    if "chapter" in filename:
        filename = f"Chapters/{filename}"
        name = filename.split("/")[1].split("_logger")[0]
    else:
        filename = filename
        name = filename.split("_logger")[0]
    log_directory = "/media/charancherry/Code/Myprojects/PythonProjects/FullStack_Projects/Linkifinity/Logs"
    log_file_name = os.path.join(
        f"{log_directory}/{filename}",
        f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    )
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)

    # Create a logger instance
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Create a file handler
    file_handler = logging.FileHandler(log_file_name)
    file_handler.setLevel(logging.INFO)

    # Create a log format
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)

    # Add the file handler to the logger
    logger.addHandler(file_handler)

    return logger


def get_page_source(manga_url) -> BeautifulSoup:
    options = Options()
    options.add_argument("--headless")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/58.0.3029.110 Safari/537"
    )
    driver = webdriver.Chrome(options=options)
    driver.get(manga_url)
    content = driver.page_source
    soup = BeautifulSoup(content, "html.parser")

    return soup


def mongodb_insertion(manga_details, collection_var, insert_logger):
    collection = get_collection(collection_var)
    logs = []

    for manga in manga_details:
        try:
            title = manga.get("Title")
            local_latest_chapters = manga.get("Latest_chapters", [])

            # Sort the chapters in descending order by chapter_num
            sorted_chapters = sorted(
                local_latest_chapters,
                key=lambda x: x.get("chapter_num", 0),
                reverse=True,
            )

            mongodb_document = collection.find_one({"Title": title})

            if mongodb_document:
                existing_chapters = mongodb_document.get("Latest_chapters", [])

                # Find new chapters that are not already in the database
                new_chapters = [
                    chapter
                    for chapter in sorted_chapters
                    if chapter not in existing_chapters
                ]
                if new_chapters:
                    logs.append(
                        f"New chapters found for '{title}' in the list. Inserting to MongoDB."
                    )
                    updated_chapters = existing_chapters + new_chapters
                    sorted_updated_chapters = sorted(
                        updated_chapters,
                        key=lambda x: x.get("chapter_num", 0),
                        reverse=True,
                    )
                    collection.update_one(
                        {"_id": mongodb_document["_id"]},
                        {"$set": {"Latest_chapters": sorted_updated_chapters}},
                    )
                else:
                    logs.append(f"No new chapters found for '{title}' in the list.")
            else:
                collection.insert_one(
                    {
                        "Title": title,
                        "Image": manga["Image"],
                        "Binary_Image": manga["Binary_Image"],
                        "Latest_chapters": sorted_chapters,
                    }
                )
                logs.append(
                    f"No matching document found in MongoDB for '{title}', New document inserted."
                )
        except Exception as e:
            insert_logger.error(f"Error occurred for manga: {title}. Error: {e}")

    for log in logs:
        insert_logger.info(log)


def validate_data(manga_details):
    for manga in manga_details:
        if not isinstance(manga["Title"], str):
            raise ValueError("Invalid Title")
        if not isinstance(manga["Image"], str):
            raise ValueError("Invalid Image")
        if not isinstance(manga["Binary_Image"], str):
            raise ValueError("Invalid Binary_Image")
        if not isinstance(manga["Latest_chapters"], list):
            raise ValueError("Invalid Latest_chapters")
        for chapter in manga["Latest_chapters"]:
            if not isinstance(chapter["chapter_num"], str | int | float):
                raise ValueError("Invalid chapter_num")
            if not isinstance(chapter["chapter_url"], str):
                raise ValueError("Invalid chapter_url")
