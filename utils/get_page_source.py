import time
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from utils.common_functions import setup_logging
from utils.database_connection import get_collection

# Initialize unified logger
logger = setup_logging(__name__)

# -------------------------------------------------------------------
# ✅ Known site mirrors (extend this easily later)
# -------------------------------------------------------------------
SITE_MIRRORS = {
    "harimanga": ["harimanga.com", "harimanga.me", "harimanga.org", "harimanga.net"],
    "kunmanga": ["kunmanga.com", "kunmanga.net"],
    "manhuaplus": ["manhuaplus.com", "manhuaplus.me", "manhuaplus.net"],
    "manhuaus": ["manhuaus.com", "manhuaus.me", "manhuaus.net"],
    "manhwaclan": ["manhwaclan.com", "manhwaclan.net", "manhwaclan.me"],
}
# -------------------------------------------------------------------


def get_active_mirror(domain_key: str) -> str | None:
    """Return first responsive mirror for a given site key."""
    mirrors = SITE_MIRRORS.get(domain_key, [])
    for domain in mirrors:
        test_url = f"https://{domain}"
        try:
            r = requests.get(test_url, timeout=5)
            if r.status_code == 200:
                logger.success(f"[{domain_key}] Active mirror found: {domain}")
                return domain
        except requests.RequestException:
            continue
    logger.error(f"[{domain_key}] No active mirror found.")
    return None


def get_page_source(manga_url: str, timeout: int = 15):
    """Fetch and store page source for any supported manga site."""
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-gpu")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0 Safari/537.36"
    )
    options.page_load_strategy = "eager"

    driver = webdriver.Chrome(options=options)
    collection = get_collection("get_page_source")

    try:
        try:
            driver.get(manga_url)
        except WebDriverException as e:
            if "ERR_NAME_NOT_RESOLVED" in str(e):
                # Identify which site key this URL belongs to
                domain_key = next(
                    (key for key in SITE_MIRRORS if key in manga_url), None
                )
                if domain_key:
                    logger.warning(f"[{domain_key}] DNS error — attempting mirror switch.")
                    active = get_active_mirror(domain_key)
                    if active:
                        # Preserve subpath after domain name
                        manga_path = manga_url.split(domain_key, 1)[-1].lstrip(".com").lstrip("/")
                        new_url = f"https://{active}/{manga_path}"
                        logger.info(f"[{domain_key}] Retrying with {new_url}")
                        driver.get(new_url)
                        manga_url = new_url  # update URL for DB entry
                    else:
                        raise Exception(f"[{domain_key}] No available mirror found.")
                else:
                    logger.error(f"Unknown site for URL: {manga_url}")
                    raise
            else:
                raise

        # Site-specific wait or delay
        if "kunmanga" in manga_url:
            time.sleep(5)

        # Wait for common elements across most manga sites
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "div.page-content-listing, div.tab-summary, div#chapterlist")
            )
        )

        html = driver.page_source
        soup = BeautifulSoup(html, "html.parser")

        # Store in DB if not already present
        if not collection.find_one({"manga_url": manga_url}):
            collection.insert_one({"manga_url": manga_url, "page_source": str(soup)})
            logger.success(f"Inserted page source for {manga_url}")
        else:
            logger.info(f"Page source already exists for {manga_url}")

        return soup

    except TimeoutException:
        logger.warning(f"Timeout while loading {manga_url} — returning partial source.")
        return BeautifulSoup(driver.page_source, "html.parser")

    except Exception as e:
        logger.error(f"Error processing {manga_url}: {e}", exc_info=True)
        return None

    finally:
        driver.quit()
