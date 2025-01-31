import datetime
import os.path
import sys
import time

from selenium import webdriver
from selenium.common import NoSuchElementException, NoSuchFrameException
from selenium.webdriver import Keys
from selenium.webdriver.common.by import By

TIMEOUT_SECONDS = 120

def switch_to_iframe_by_id(driver, iframe_id):
    iframe_found = False
    count = 0
    while not iframe_found:
        if count > TIMEOUT_SECONDS:
            print("Timed out waiting for iframe to appear")
            return False

        try:
            iframe = driver.find_element(By.ID, iframe_id)
            iframe_found = True

            driver.switch_to.frame(iframe)

            return True
        except NoSuchElementException:
            count += 1
            pass

        time.sleep(1)

def cleanup_windows(driver):
    if len(driver.window_handles) > 1:
        for i in range(len(driver.window_handles) - 1, 1, -1):
            driver.switch_to.window(driver.window_handles[i])

            driver.close()

def main():
    if len(sys.argv) != 2 and len(sys.argv) != 3:
        print("Usage: thscscraper.py <url> <download directory> (Optional)")
        return

    thsc_link = sys.argv[1]
    print("Using thsc link: " + thsc_link)

    download_dir = None
    if len(sys.argv) == 3:
        download_dir = sys.argv[2]

        if not os.path.isdir(download_dir):
            print("Error: Please use a valid directory")
            return

    start_time = datetime.datetime.now().replace(microsecond=0)

    firefox_options = webdriver.FirefoxOptions()
    firefox_options.set_preference("browser.download.manager.showWhenStarting", False)
    firefox_options.add_argument("--headless")
    if download_dir is not None:
        firefox_options.set_preference("browser.download.folderList", 2)
        firefox_options.set_preference("browser.download.dir", sys.argv[2])
    else:
        firefox_options.set_preference("browser.download.folderList", 1)

    driver = webdriver.Firefox(options=firefox_options)
    driver.get("https://thsconline.github.io/s/yr12/Maths/trialpapers_general.html")
    download_count = 0

    links = driver.find_elements(By.TAG_NAME, "a")
    paper_link_found = False
    for index, link in enumerate(links):
        paper_name = link.text
        if not paper_link_found:
            link_text = link.text
            if link_text == "upload files here":
                paper_link_found = True
        else:
            original_window = driver.current_window_handle
            time_now = datetime.datetime.now().replace(microsecond=0)

            print("Entering: " + paper_name)
            print("Elapsed time: " + str(time_now - start_time))
            link.click()

            driver.switch_to.window(driver.window_handles[1])

            if not switch_to_iframe_by_id(driver, "viewer"):
                continue

            if not switch_to_iframe_by_id(driver, "sandboxFrame"):
                continue

            if not switch_to_iframe_by_id(driver, "userHtmlFrame"):
                continue

            download_button_found = False
            download_button = None
            count = 0
            while not download_button_found:
                if count > 120:
                    print("Timed out waiting for download button to appear")
                    break

                try:
                    download_button = driver.find_element(By.ID, "download")

                    download_button_found = True
                except NoSuchElementException:
                    count += 1
                    pass

                time.sleep(1)

            if download_button:
                download_button.click()
                download_count += 1

                print("Downloaded: " + paper_name)
                print("Download Count: " + str(download_count))

                driver.switch_to.default_content()

                cleanup_windows(driver)

                driver.switch_to.window(original_window)

main()
