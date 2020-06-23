import re
import time

def has_html_elements(check_string):
    """
    :param check_string: any string you want to check against HTML tags
    :return : True if any HTML tags are found inside string
    """
    if isinstance(check_string, str) :
        matches =  re.search("<p|<span|<div|<a|<body|<h2|<h1",check_string)
        if matches :
            return True

    return False

def scroll_down(driver, n_times):
    """
    Helper function to navigate to the bottom of a web page, and to scroll down further by a specific number of times
    :param driver: The selenium webdriver
    :param n_times: The number of times we want to scroll down
    """
    SCROLL_PAUSE_TIME = 0.5

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    for i in range(1,n_times) :
        # Scroll down to bottom
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

        # Wait to load page
        time.sleep(SCROLL_PAUSE_TIME)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height