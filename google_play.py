import time
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

def get_top():
    print('debug browser')
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--headless')

    driver = webdriver.Chrome(chrome_options=chrome_options)
    print('driver created')

    google_play_top_grossing_url = 'https://play.google.com/store/apps/collection/cluster?clp=0g4YChYKEHRvcGdyb3NzaW5nX0dBTUUQBxgD:S:ANO1ljLhYwQ&gsr=ChvSDhgKFgoQdG9wZ3Jvc3NpbmdfR0FNRRAHGAM%3D:S:ANO1ljIKta8'
    driver.get(google_play_top_grossing_url)

    # scroll_down(driver, 5)

    # Every xPath relative to game entry
    top_100_games = []
    game_link_xpath = '/div[2]/div/div/div[1]/div/div/div[1]/a'
    game_title_xpath = '/div[2]/div/div/div[1]/div/div/div[1]/a/div'

    # TOP 50
    top_50_xpath = '/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/div[{game_index}]/c-wiz/div/div'
    for i in range(1,5) :
        link_element = driver.find_element_by_xpath(top_50_xpath.format(game_index=i) + game_link_xpath)
        title_element = driver.find_element_by_xpath(top_50_xpath.format(game_index=i) + game_title_xpath)

        top_100_games.append({
            'rank' : i,
            'name' : title_element.get_attribute('title'),
            'app_url' : link_element.get_attribute('href')
        })

    # TOP 50-100
    # top_50_plus_xpath = '/html/body/div[1]/div[4]/c-wiz/div/c-wiz/div/c-wiz/c-wiz/c-wiz/div/div[2]/c-wiz[{game_index}]/div/div'
    # for i in range(1,51) :
    #     link_element = driver.find_element_by_xpath(top_50_plus_xpath.format(game_index=i) + game_link_xpath)
    #     title_element = driver.find_element_by_xpath(top_50_plus_xpath.format(game_index=i) + game_title_xpath)
    #
    #     top_100_games.append({
    #         'rank': i+50,
    #         'name': title_element.get_attribute('title'),
    #         'app_url': link_element.get_attribute('href')
    #     })

    return driver, top_100_games

def get_top_details(driver, top_results):
    main_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[1]/c-wiz[1]/div'
    icon_sub_xpath = '/div[1]/div/img'
    publisher_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[1]/div[1]/span[1]/a'
    publisher_2_sub_xpath = '/div[2]/div/div[1]/div[2]/div[1]/div[1]/span[1]/a'
    category_1_sub_xpath = '/div[2]/div/div[1]/div[1]/div[1]/div[1]/span[2]/a'
    category_2_sub_xpath = '/div[2]/div/div[1]/div[2]/div[1]/div[1]/span[2]/a'

    # This seems to load "externally"
    additional_info_frame_xpath = '/html/body/div[1]/div[4]/c-wiz[1]/div/div[2]/div/div[1]/div/c-wiz[3]'
    num_installs_sub_xpath = '/div[1]/div[2]/div/div[3]/span/div/span'
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
        'num_installs': WebElement(additional_info_frame_xpath + num_installs_sub_xpath, 'innerHTML'),
        'last_updated_date': WebElement(additional_info_frame_xpath + last_updated_sub_xpath, 'innerHTML'),
        'ratings_num_1': WebElement(review_frame_xpath + ratings_num_1_sub_xpath, 'aria-label'),
        'ratings_num_2': WebElement(ratings_num_2_sub_xpath, 'aria-label'),
        'ratings_score_1': WebElement(review_frame_xpath + ratings_score_1_sub_xpath, 'innerHTML'),
        'ratings_score_2': WebElement(ratings_score_2_sub_xpath, 'innerHTML'),
    }

    for app in top_results :
        driver.get(app['app_url'])

        # Wait for extra sections of the page to load
        try:
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, additional_info_frame_xpath)))
            WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.XPATH, review_frame_xpath)))
        except TimeoutException:
            print('Installs element failed to load')

        for key, element in elements.items() :
            try:
                cur_element = driver.find_element_by_xpath(element.xpath)
                app[key] = cur_element.get_attribute(element.attribute)
            except NoSuchElementException:
                pass

        # print('Ratings frame attribute: {}'.format(driver.find_element_by_xpath(ratings_frame).get_attribute('aria-label')))

        app['icon_url'] = app.get('icon')
        app['publisher_name'] = app.get('publisher_2') if app.get('publisher_1') is None else app.get('publisher_1')
        app['category'] = app.get('category_2') if app.get('category_1') is None else app.get('category_1')
        app['ratings_num'] = app.get('ratings_num_2') if app.get('ratings_num_1') is None else app.get('ratings_num_1')
        app['ratings_score'] = app.get('ratings_score_2') if app.get('ratings_score_1') is None else app.get('ratings_score_1')
        app['num_installs'] = app.get('num_installs')
        app['last_updated_date'] = app.get('last_updated_date')

    return top_results

driver, top_results = get_top()
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

for key, value in empty_fields.items():
    print('Total number of empty {}:{}'.format(key, value))

#Total number of empty num_installs:1
#Total number of empty ratings_num:18
#Total number of empty ratings_score:18
#Total number of empty category:0
