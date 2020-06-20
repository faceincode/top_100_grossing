#/home/ralcantara/workspace/data_mining/top_100_grossing/venv/bin/python
import time
import json
import datetime
from collections import namedtuple
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException

WebElement = namedtuple('WebElement','xpath attribute')

def scroll_down(driver, n_times):
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

def get_top(test=False):
    print('debug browser')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    print('driver created')

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

    # TOP 50
    top_50_xpath = '/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/div[{game_index}]/c-wiz/div/div'
    for i in range(min_max_minibatch_range[0],min_max_minibatch_range[1]) :
        link_element = driver.find_element_by_xpath(top_50_xpath.format(game_index=i) + game_link_xpath)
        title_element = driver.find_element_by_xpath(top_50_xpath.format(game_index=i) + game_title_xpath)

        top_apps.append({
            'rank' : i,
            'name' : title_element.get_attribute('title'),
            'app_url' : link_element.get_attribute('href')
        })

    min_max_batch_range = (1,19)
    if test == True :
        min_max_batch_range = (0,1)

    # Batch download 50 apps at a time
    for j in range(min_max_batch_range[0],min_max_batch_range[1]) :
        scroll_down(driver, 5)

        # TOP 50-100
        top_50_plus_xpath = '/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/c-wiz[{game_index}]/div/div'
        for i in range(min_max_minibatch_range[0],min_max_minibatch_range[1]) :
            link_element = driver.find_element_by_xpath(top_50_plus_xpath.format(game_index=i) + game_link_xpath)
            title_element = driver.find_element_by_xpath(top_50_plus_xpath.format(game_index=i) + game_title_xpath)

            top_apps.append({
                'rank': i+50 + (j*50),
                'name': title_element.get_attribute('title'),
                'app_url': link_element.get_attribute('href')
            })

    return driver, top_apps

def get_top_details(driver, top_results):
    main_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[1]/c-wiz[1]/div'
    icon_sub_xpath = '/div[1]/div/img'
    publisher_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[1]/div[1]/span[1]/a'
    publisher_2_sub_xpath = '/div[2]/div/div[1]/div[2]/div[1]/div[1]/span[1]/a'
    category_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[1]/div[1]/span[2]/a'
    category_2_sub_xpath = '/div[2]/div/div[1]/div[2]/div[1]/div[1]/span[2]/a'

    # This seems to load "externally"
    additional_info_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[3]'
    num_installs_1_sub_xpath = '/div[1]/div[2]/div/div[3]/span/div/span'
    num_installs_2_sub_xpath = '/html/body/div[1]/div[4]/c-wiz/div/div[2]/div/div[1]/div/c-wiz[2]/div[1]/div[2]/div/div[3]/span/div/span'
    last_updated_sub_xpath = '/div[1]/div[2]/div/div[1]/span/div/span'

    # Ratings & Reviews also loads "externally"
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

    for app in top_results :
        driver.get(app['app_url'])

        # Wait for extra sections of the page to load
        try:
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, additional_info_frame_xpath)))
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, review_frame_xpath)))
        except TimeoutException:
            print('Installs element failed to load')

        app_details = {}
        for key, element in elements.items() :
            try:
                cur_element = driver.find_element_by_xpath(element.xpath)
                app_details[key] = cur_element.get_attribute(element.attribute)
            except NoSuchElementException:
                pass

        # print('Ratings frame attribute: {}'.format(driver.find_element_by_xpath(ratings_frame).get_attribute('aria-label')))

        app['icon_url'] = app_details.get('icon')
        app['publisher_name'] = app_details.get('publisher_2') if app_details.get('publisher_1') is None else app_details.get('publisher_1')
        app['category'] = app_details.get('category_2') if app_details.get('category_1') is None else app_details.get('category_1')
        app['ratings_num'] = app_details.get('ratings_num_2') if app_details.get('ratings_num_1') is None else app_details.get('ratings_num_1')
        app['ratings_score'] = app_details.get('ratings_score_2') if app_details.get('ratings_score_1') is None else app_details.get('ratings_score_1')
        app['num_installs'] = app_details.get('num_installs_2') if app_details.get('num_installs_1') is None else app_details.get('num_installs_1')
        app['last_updated_date'] = app_details.get('last_updated_date')

    return top_results

driver, top_results = get_top(test=True)
top_results_detailed = get_top_details(driver, top_results)

for app in top_results_detailed :
    # print('Rank: {} || Name: {} || Category: {} || Rating: {} || Num Installs: {} || Num Reviews: {}'.format(
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

empty_fields = {
    'num_installs': 0,
    'ratings_num': 0,
    'ratings_score': 0,
    'category': 0
}

for app in top_results_detailed :
    for key, value in empty_fields.items() :
        if app[key] == None :
            empty_fields[key] += 1

# APP: Epic Seven (39,40)
# Ratings Score is messed up - has a long div/div/div hierarchy
# Num installs isn't working
for key, value in empty_fields.items():
    print('Total number of empty {}:{}'.format(key, value))

# Utility Functions
def get_todays_date():
    today = datetime.date.today()
    today = str(today).replace('-', '_')
    return today

def get_todays_month():
    today = datetime.date.today()
    return today.month

def get_todays_year():
    today = datetime.date.today()
    return today.year

def save_record_to_json(file_path, record):
    with open(file_path, "w") as f:
        json.dump(record, f)

# Process all app_url records, and save them to their respective location
def save_daily_record(app_list):
    date = get_todays_date()

    file_name = 'top_grossing_android_{}.json'.format(date)

    # Save the record in the app_id's monthly directory
    save_record_to_json('./output/{}'.format(file_name), app_list)

save_daily_record(top_results)
