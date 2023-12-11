import logging
import os
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

from utils.database_connection import get_collection


def delete_collection_records():
    collection_name = get_collection("get_manga_details")
    collection_name.delete_many({})


def setup_logging(filename):
    log_directory = "/media/charan/code/Myprojects/PythonProjects/Linkifinity/Logs"
    log_file_name = os.path.join(
        f"{log_directory}/{filename}",
        f"log_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log",
    )
    os.makedirs(os.path.dirname(log_file_name), exist_ok=True)

    # Create a logger instance
    logger = logging.getLogger(__name__)
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


def mongodb_insertion(manga_details, collection_var, logfile):
    logger = setup_logging(logfile)
    collection = get_collection(collection_var)
    logs = []
    for manga in manga_details:
        try:
            logs.append(f"Inserting manga: {manga['Title']}")
            local_latest_chapter = manga["Latest_chapters"][0]["chapter_num"]
            mongodb_document = collection.find_one({"Title": manga["Title"]})
            if mongodb_document:
                mongodb_latest_chapter = mongodb_document["Latest_chapters"][0]["chapter_num"]
                if float(local_latest_chapter) > float(mongodb_latest_chapter):
                    logs.append(
                        f"""Updated latest chapter in MongoDB for '{manga['Title']}': 
                                {mongodb_latest_chapter} -> {local_latest_chapter}"""
                    )
                    collection.update_one(
                        {"_id": mongodb_document["_id"]},
                        {"$set": {"Latest_chapters": manga["Latest_chapters"]}},
                    )
                else:
                    logs.append(
                        f"""No update needed for '{manga['Title']}' in MongoDB. Local: {local_latest_chapter},
                         MongoDB: {mongodb_latest_chapter}"""
                    )
            else:
                collection.insert_one(manga)
                logs.append(f"No matching document found in MongoDB for '{manga['Title']}'")
                logs.append(f"New document inserted for '{manga['Title']}'")
        except IndexError as e:
            logger.error(f"IndexError occurred for manga: {manga['Title']}. Error: {e}")
    for log in logs:
        logger.info(log)


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
