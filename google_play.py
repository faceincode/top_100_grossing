import argparse
import time
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from utils.record_utils import get_todays_date, save_record_to_json
from utils.selenium_utils import has_html_elements, scroll_down
from utils.system_utils import send_error_report, str2bool

# TODO - Useful functionality:
# Containerize project so I can run from bash on a cron job
# Eliminate any funny chromedriver / dependency issues
# Docker run should output to local folder
# Clean up element XPATH/Element/Attribute code
# Data workflow will be responsible for managing I/O
# Add e-mail alert on any bad data so I can fix it...
    # or level up and build out workflow in Airflow
# If this starts failing, update logic to resume daily activity from where it left off.
def get_top_app_records(test=False):
    """
    Returns the top X products in the top grossing list.
    This could likely be abstracted to pass in any list from GP and extracted.

    :param test: Pass 'True' if you want to debug this function, and only process a few items from the top_1000_list.
    :return driver, top_apps:
    driver: The selenium webdriver that is used to navigate all urls
    top_apps: A list of apps, ranked in order, with all needed information to scrape information from each one.
    """

    # Setup a headless driver so no browser pops up.
    # Disabled a couple of other settings that were causing local browser to crash
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options=chrome_options)

    # Points directly to
    google_play_top_grossing_url = 'https://play.google.com/store/apps/collection/cluster?clp=0g4YChYKEHRvcGdyb3NzaW5nX0dBTUUQBxgD:S:ANO1ljLhYwQ&gsr=ChvSDhgKFgoQdG9wZ3Jvc3NpbmdfR0FNRRAHGAM%3D:S:ANO1ljIKta8'
    driver.get(google_play_top_grossing_url)

    # Every xPath relative to game entry
    top_apps = []
    game_link_xpath = '/div[2]/div/div/div[1]/div/div/div[1]/a'
    game_title_xpath = '/div[2]/div/div/div[1]/div/div/div[1]/a/div'

    # Minibatch = Inner Loop = 50 records
    # Batch = Outer Loop = 1000 records loop
    min_max_minibatch_range = (1,50)
    if test == True :
        min_max_minibatch_range = (1,2)

    # TOP 50 items
    # We actually go from 1-49 as the 50th item, uses a different XPath
    # We simply increment the game_index value, to access each app on GP
    top_50_xpath = '/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/div[{game_index}]/c-wiz/div/div'
    for i in range(min_max_minibatch_range[0],min_max_minibatch_range[1]) :
        link_element = driver.find_element_by_xpath(top_50_xpath.format(game_index=i) + game_link_xpath)
        title_element = driver.find_element_by_xpath(top_50_xpath.format(game_index=i) + game_title_xpath)

        top_apps.append({
            'rank' : i,
            'name' : title_element.get_attribute('title'),
            'app_url' : link_element.get_attribute('href')
        })

    # This is setting up an outer loop, that defines how many batches of 50 apps we're going to download
    min_max_batch_range = (1,19)
    if test == True :
        min_max_batch_range = (0,1)

    # Batch download 50 apps at a time, and does this multiple times
    for next_50_index in range(min_max_batch_range[0],min_max_batch_range[1]) :
        # We scroll down the web page as needed, to load the next 50 apps
        scroll_down(driver, 5)

        # TOP 50+ XPath index.
        # {game_index} is incremented to access 1 through 50th app in this segment
        top_50_plus_xpath = '/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/c-wiz[{game_index}]/div/div'
        for i in range(min_max_minibatch_range[0],min_max_minibatch_range[1]) :
            link_element = driver.find_element_by_xpath(top_50_plus_xpath.format(game_index=i) + game_link_xpath)
            title_element = driver.find_element_by_xpath(top_50_plus_xpath.format(game_index=i) + game_title_xpath)

            top_apps.append({
                # We've already gone through 49 items, so our base index is 50.
                'rank': 50 + (next_50_index*50) + i,
                'name': title_element.get_attribute('title'),
                'app_url': link_element.get_attribute('href')
            })

    return driver, top_apps

# We are going to define a named tuple to make it easier to setup our scraper
WebElement = namedtuple('WebElement','xpath attribute')

def get_app_details(driver, top_results):
    """
    Responsible for setting up the Web Elements->Attributes that will be extracted from each game
    The XPath between each product varies a bit. This set of rules seems to encompass all top 1000 grossing games.

    :param driver: The webdriver
    :param top_results: The list of apps we want to scrape. Obtained from calling get_top(). This is updated by this function, with all info gathered.
    """

    main_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[1]/c-wiz[1]/div'
    icon_sub_xpath = '/div[1]/div/img'
    publisher_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[1]/div[1]/span[1]/a'
    publisher_2_sub_xpath = '/div[2]/div/div[1]/div[2]/div[1]/div[1]/span[1]/a'
    category_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[1]/div[1]/span[2]/a'
    category_2_sub_xpath = '/div[2]/div/div[1]/div[2]/div[1]/div[1]/span[2]/a'

    # This loads late # 1- Install & Date information (very bottom of app page)
    additional_info_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[3]'
    num_installs_1_sub_xpath = '/div[1]/div[2]/div/div[3]/span/div/span'
    num_installs_2_sub_xpath = '/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div[1]/div/c-wiz[2]/div[1]/div[2]/div/div[3]/span/div/span'
    last_updated_sub_xpath = '/div[1]/div[2]/div/div[1]/span/div/span'

    # This loads late # 2 - Ratings & Reviews (very top of app page)
    review_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[1]/c-wiz[1]/div'
    ratings_num_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[2]/c-wiz/span/span[1]'
    ratings_num_2_sub_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[1]/c-wiz[1]/div/div[2]/div/div[1]/div[2]/div[2]/c-wiz/span/span[1]'
    ratings_score_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[2]/c-wiz/div/div'
    ratings_score_2_sub_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[1]/c-wiz[1]/div/div[2]/div/div[1]/div[2]/div[2]/c-wiz/div/div'

    elements = {
        'icon': WebElement(main_frame_xpath + icon_sub_xpath, 'src'),
        'publisher_1': WebElement(main_frame_xpath + publisher_1_sub_xpath, 'innerHTML'),
        'publisher_2': WebElement(main_frame_xpath + publisher_2_sub_xpath, 'innerHTML'),
        'category_1': WebElement(main_frame_xpath + category_1_sub_xpath, 'text'),
        'category_2': WebElement(main_frame_xpath + category_2_sub_xpath, 'text'),
        'num_installs_1': WebElement(additional_info_frame_xpath + num_installs_1_sub_xpath, 'innerHTML'),
        'num_installs_2': WebElement(num_installs_2_sub_xpath, 'innerHTML'),
        'last_updated_date': WebElement(additional_info_frame_xpath + last_updated_sub_xpath, 'innerHTML'),
        'ratings_num_1': WebElement(review_frame_xpath + ratings_num_1_sub_xpath, 'aria-label'),
        'ratings_num_2': WebElement(ratings_num_2_sub_xpath, 'aria-label'),
        'ratings_score_1': WebElement(review_frame_xpath + ratings_score_1_sub_xpath, 'aria-label'),
        'ratings_score_2': WebElement(ratings_score_2_sub_xpath, 'aria-label'),
    }

    # For every game we look into it's URL
    for app in top_results :
        driver.get(app['app_url'])

        # Wait for Install & Ratings sections to load
        try:
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, additional_info_frame_xpath)))
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, review_frame_xpath)))
        except TimeoutException:
            print('Installs element failed to load')

        # We then want to extract all the data from the elements we care about
        app_details = {}
        for key, element in elements.items() :
            try:
                cur_element = driver.find_element_by_xpath(element.xpath)
                app_details[key] = cur_element.get_attribute(element.attribute)
            except NoSuchElementException:
                pass

        # We then collect all the data from the HTML elements/attributes we scraped
        app['icon_url'] = app_details.get('icon')
        app['publisher_name'] = app_details.get('publisher_2') if app_details.get('publisher_1') is None else app_details.get('publisher_1')
        app['category'] = app_details.get('category_2') if app_details.get('category_1') is None else app_details.get('category_1')
        app['ratings_num'] = app_details.get('ratings_num_2') if app_details.get('ratings_num_1') is None else app_details.get('ratings_num_1')
        app['ratings_score'] = app_details.get('ratings_score_2') if app_details.get('ratings_score_1') is None else app_details.get('ratings_score_1')
        app['num_installs'] = app_details.get('num_installs_2') if app_details.get('num_installs_1') is None else app_details.get('num_installs_1')
        app['last_updated_date'] = app_details.get('last_updated_date')

def check_errors(top_results_detailed):
    """
    NUmber of fields that are empty
    Number of fields that might hae extracted HTML (i.e. check for <div> <span> etc...)

    :param top_results_detailed: Pass in the final list of top_results_detailed
    :return: None. E-mail is sent to mailing list, if errors are found.
    TODO - Improve alarms as data workflow improves
    """

    # We track any major empty_fields inside of the top_app_results
    scraping_errors = {
        'rank' : 0,
        'name' : 0,
        'app_url' : 0,
        'icon_url' : 0,
        'pubisher_name' : 0,
        'category' : 0,
        'ratings_num' : 0,
        'ratings_score' : 0,
        'num_installs' : 0,
        'last_updated_date' : 0,
        'error_html_scrapes' : 0,
        'error_apps': {}
    }

    errors_encountered = False
    for app in top_results_detailed :
        for key, value in app.items() :
            if app[key] is None:
                scraping_errors[key] += 1
                scraping_errors['error_apps'][app['name']] = 1
                errors_encountered = True
            elif has_html_elements(app[key]) == True :
                scraping_errors['html_scrapes'] += 1
                scraping_errors['error_apps'][app['name']] = 1
                errors_encountered = True

    if errors_encountered == True :
        error_list = []
        for key, value in scraping_errors.items():
            if not key in ('error_html_scrapes','error_apps'):
                error_list.append('Total number of empty {}:{}'.format(key, value))
            else:
                error_list.append('{}: {}'.format(key, value))

        send_error_report(error_list)
    else:
        print("SUCCESS: Data checked. Found no issues.")

def save_daily_record(app_list):
    """
    Saves all records to json file in ./output/ folder
    """
    date = get_todays_date()

    file_name = 'top_grossing_android_{}.json'.format(date)

    # Save the record in the app_id's monthly directory
    save_record_to_json('./output/{}'.format(file_name), app_list)

def main():
    """
    :args test: True/False Use this to process only a few apps.
    :return:
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('--test', type=str2bool, default=False, nargs='?',  const=True , required=False, help="Tests 2-3 apps")
    args = parser.parse_args()

    driver, top_results = get_top_app_records(test=args.test)
    get_app_details(driver, top_results)

    if args.test == True :
        for app in top_results :
            # We print all the apps into the console so we can verify the output
            print('Rank: {} || Name: {} || Num Installs: {} || Ratings: {} || Score: {} || Category: {} || Publisher: {} || Last Updated Date: {} || App Url: {}'.format(
                app['rank'],
                app['name'],
                app['num_installs'],
                app['ratings_num'],
                app['ratings_score'],
                app['category'],
                app['publisher_name'],
                app['last_updated_date'],
                app['app_url']
            ))

    check_errors(top_results)
    save_daily_record(top_results)

if __name__ == "__main__":
    main()