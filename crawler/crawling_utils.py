import time
import os
from selenium import webdriver  # Import from seleniumwire
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
from cleantext import clean
import multiprocessing as mp
import tqdm
import pandas as pd

list_to_empty_token = ["Digimon Reference Book",
                       "Video Games Misc", "Anime & Manga", "\n"]


def init_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--headless")
    options.add_argument("--log-level=3")
    driver = webdriver.Chrome(options=options)
    return driver


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
    # print("CURRENT URL %s" % url_page)
    driver.get(url_page)
    time.sleep(1)
    # DESCRIPTION
    desc_tag = "//table//tbody//tr//td[@valign=\"top\"]"
    wait_until_xpath(driver, desc_tag)
    description_td = driver.find_elements(
        By.XPATH, desc_tag)
    # print([x.text for x in description_td])
    # THIS TOKENIZATION IS CORRECT, THE FAILS ARE RELATED TO DIGIMON PAGES WITH NO DESCRIPTION,
    # THAT WILL BE SKIPPED
    description = [x.text for x in description_td if hasattr(
        x, "text") and "⇨ Japanese" in x.text]

    # mege the text
    description = " ".join(description)
    description = "".join(description.split("⇨ Japanese")[1])
    description = clean(description)
    for bw in list_to_empty_token:
        # lower because i previously cleaned the sentence
        description = description.replace(bw.lower(), "").strip()

    # IMAGE
    image_desc = "//tbody//tr//td[@colspan=\"4\"]//div//div//a[@class=\"image\"]//img"
    image_url = driver.find_element(By.XPATH, image_desc).get_attribute("src")
    image_url = os.path.basename(image_url)
    # print(image_url)
    if "-" in image_url:
        image_url = "-".join(os.path.basename(image_url).split("-")[1:])
    real_basename = image_url
    image_url = "https://wikimon.net/File:" + image_url
    # print(image_url)
    # IMAGE PAGE
    driver.get(image_url)
    desc_tag = "//div[@class=\"fullImageLink\"]//a"
    wait_until_xpath(driver, desc_tag)
    time.sleep(1)
    image_file_url = driver.find_element(
        By.XPATH, desc_tag).get_attribute("href")
    # print(image_file_url)
    image_path = "%s/%s" % (download_image_root, real_basename)
    download_image(image_file_url, image_path)
    return real_basename, image_url, description


def crawl_data(pairs, download_image_root):
    driver = init_driver()
    fails = []
    dataset = pd.DataFrame(columns=[
                           "name", "full_page_wiki_url", "image_url", "image_filename", "description"])
    for (name, url_page) in tqdm.tqdm(pairs, total=len(pairs), desc="Retrieving Image and Text"):
        try:
            image_path, image_url, description = get_image_text_from_url(
                driver, url_page, name, download_image_root)
            new_row = {"name": name, "full_page_wiki_url": url_page, "image_url": image_url,
                       "image_filename": image_path, "description": description}
            dataset = dataset.append(new_row, ignore_index=True)
            # dataset.to_csv(df_path, index=False)

        except Exception as e:
            print(e)
            fails.append((name, url_page))
            # with open("dataset/fails.txt", "w") as f:
            #     for x in fails:
            #         f.write(",".join(x) + "\n")
    return dataset, fails


def create_driver_parallel_crawling(pairs, download_image_root, df_path):
    # TO DEBUG
    # pairs = pairs[-8:]
    # cp_count = 2  # mp.cpu_count()
    cp_count = mp.cpu_count()
    print(cp_count)
    partition_len = len(pairs)//cp_count
    pool = mp.Pool(cp_count)
    partitions = [pairs[i:(i+partition_len)]
                  for i in range(0, len(pairs), partition_len)]
    results = pool.starmap(
        crawl_data, [(part, download_image_root) for part in partitions])
    pool.close()

    # AGGREGATE AND SAVE RESULTS
    df_final = pd.DataFrame(columns=[
                            "name", "full_page_wiki_url", "image_url", "image_filename", "description"])
    tot_failures = []
    for res in results:
        df_temp, failures = res
        df_final = df_final.append(df_temp, ignore_index=True)
        tot_failures.extend(failures)
    
    df_final.to_csv(df_path, index=False)


    with open("dataset/fails.txt", "w", encoding="utf-8") as f:
        for x in tot_failures:
            f.write(",".join(x) + "\n")

