import warnings
warnings.filterwarnings("ignore")
from selenium import webdriver  # Import from seleniumwire
from selenium.webdriver.common.by import By
import crawling_utils
import pandas as pd
import tqdm
import time
from tqdm.contrib import tzip
import traceback

if __name__=="__main__":
    driver = crawling_utils.init_driver()
    download_image_root = "dataset/images/"
    df_path = "dataset/digimon_dataset.csv"


    web_site_url = "https://wikimon.net/Visual_List_of_Digimon"
    driver.get(web_site_url)

    # GET ALL IMAGES WITH LINKS OF THE DIGILIST
    tag_images = "//a//img[@decoding=\"async\"]"
    crawling_utils.wait_until_xpath(driver, tag_images)
    digimon_a_href = driver.find_elements(By.XPATH, tag_images)

    print(len(digimon_a_href))

    dataset = pd.DataFrame(
        columns=["name", "full_page_wiki_url", "image_url", "image_filename", "description"])

    pairs = []
    for el in tqdm.tqdm(digimon_a_href, total=len(digimon_a_href), desc="parsing urls"):
        name = el.get_attribute("alt")
        if len(name.split()) > 1:
            name = name.split()[0] + "_" + " ".join(name.split()[1:])
        url_page = "https://wikimon.net/%s" % name
        pairs.append((name, url_page))


    driver.close()
    crawling_utils.create_driver_parallel_crawling(pairs,download_image_root)

# fails = []
# for (name, url_page) in tqdm.tqdm(pairs, total=len(pairs), desc="Retrieving Image and Text"):
#     try:
#         image_path, image_url, description = crawling_utils.get_image_text_from_url(
#             driver, url_page, name, download_image_root)
#         new_row = {"name": name, "full_page_wiki_url": url_page, "image_url": image_url,
#                                  "image_filename": image_path, "description": description}
#         dataset = dataset.append(new_row, ignore_index=True)
#         dataset.to_csv(df_path, index=False)

#     except Exception as e:
#         print(e)
#         fails.append((name, url_page))
#         with open("dataset/fails.txt", "w") as f:
#             for x in fails:
#                 f.write(",".join(x) + "\n")