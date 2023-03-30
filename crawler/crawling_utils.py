import time
import os
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib.request
import requests


def wait_until_xpath(driver, xpath, delay=3):
    delay = delay  # seconds
    try:
        WebDriverWait(driver, delay).until(
            EC.presence_of_element_located((By.XPATH, xpath)))
        return True
    except Exception:
        return False


def download_image(url, image_path_save):
    r = requests.get(url)
    with open(image_path_save, 'wb') as outfile:
        outfile.write(r.content)


def get_image_text_from_url(driver, url_page, name, download_image_root):
    driver.get(url_page)
    time.sleep(1)
    # DESCRIPTION
    desc_tag = "//table//tbody//tr//td[@valign=\"top\"]"
    wait_until_xpath(driver, desc_tag)
    description_td = driver.find_elements(
        By.XPATH, desc_tag)
    description = [x.text for x in description_td if hasattr(
        x, "text") and "⇨ Japanese" in x.text]
    description = description[0].split("\n")
    i = description.index("⇨ Japanese")
    description = " ".join(
        description[i+1:]).replace("Digimon Reference Book", "").strip()

    # IMAGE
    image_desc = "//tbody//tr//td[@colspan=\"4\"]//div//div//a[@class=\"image\"]//img"
    image_url = driver.find_element(By.XPATH, image_desc).get_attribute("src")
    image_url = os.path.basename(image_url)

    print(image_url)
    if "-" in image_url:
        image_url = "-".join(os.path.basename(image_url).split("-")[1:])
    real_basename = image_url
    image_url = "https://wikimon.net/File:" + image_url
    print(image_url)
    # IMAGE PAGE
    driver.get(image_url)
    desc_tag = "//div[@class=\"fullImageLink\"]//a"
    wait_until_xpath(driver, desc_tag)
    time.sleep(1)
    image_file_url = driver.find_element(
        By.XPATH, desc_tag).get_attribute("href")
    print(image_file_url)
    image_path = "%s/%s" % (download_image_root,real_basename) 
    download_image(image_file_url, image_path)
    return real_basename, image_url, description
