from selenium.webdriver.chrome.options import Options
from seleniumwire import webdriver as seleniumwire_webdriver
from image_downloader import download_image
from selenium.common.exceptions import WebDriverException
import traceback
import random
import time
import re
import os
import psycopg2

# Testing Time Delay
time_delay = random.uniform(15, 25)
# Database connection parameters
db_params = {
    'dbname': 'webscraper_dev_db',
    'user': 'dev',
    'password': 'Pineapple123!',
    'host': 'localhost',
    'port': '5432'
}

# Function to connect to the database
def connect_to_db():
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection successful.")
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        return None

def sanitize_user_agent(user_agent):
    pattern = r'[a-zA-Z0-9_\s\(\)\[\]\{\}\.,;:/\\\-\+=\?\!@#\$%\^&\*`~\'\"<>|]*'
    return re.sub(pattern, '', user_agent)

def choose_random_row(conn, column, table_name):
    select_query = f"""
    SELECT {column} FROM {table_name}
    ORDER BY RANDOM()
    LIMIT 1;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(select_query)
        random_row = cursor.fetchone()
        cursor.close()
        if random_row:
            return random_row
        else:
            return None
    except Exception as e:
        print(f"Error selecting random row from {table_name}: {e}")
        return None

def choose_random_line_reservoir_sampling(file_path):
    random_line = None
    with open(file_path, 'r') as file:
        for i, line in enumerate(file):
            if random.randint(0, i) == 0:
                random_line = line
    return random_line

def update_user_data(conn, username, profile_pic_url, image_urls):
    update_query = """
    UPDATE usernames
    SET profile_pic = COALESCE(%s, profile_pic),
        image_1 = COALESCE(%s, image_1),
        image_2 = COALESCE(%s, image_2),
        image_3 = COALESCE(%s, image_3),
        image_4 = COALESCE(%s, image_4),
        image_5 = COALESCE(%s, image_5),
        image_6 = COALESCE(%s, image_6),
        image_7 = COALESCE(%s, image_7),
        image_8 = COALESCE(%s, image_8),
        image_9 = COALESCE(%s, image_9),
        image_10 = COALESCE(%s, image_10),
        image_11 = COALESCE(%s, image_11),
        image_12 = COALESCE(%s, image_12)
    WHERE u = %s;
    """
    try:
        cursor = conn.cursor()
        cursor.execute(update_query, (
            profile_pic_url,
            image_urls[0] if len(image_urls) > 0 else None,
            image_urls[1] if len(image_urls) > 1 else None,
            image_urls[2] if len(image_urls) > 2 else None,
            image_urls[3] if len(image_urls) > 3 else None,
            image_urls[4] if len(image_urls) > 4 else None,
            image_urls[5] if len(image_urls) > 5 else None,
            image_urls[6] if len(image_urls) > 6 else None,
            image_urls[7] if len(image_urls) > 7 else None,
            image_urls[8] if len(image_urls) > 8 else None,
            image_urls[9] if len(image_urls) > 9 else None,
            image_urls[10] if len(image_urls) > 10 else None,
            image_urls[11] if len(image_urls) > 11 else None,
            username
        ))
        conn.commit()
        cursor.close()
        print(f"User data for {username} updated successfully.")
    except Exception as e:
        print(f"Error updating user data for {username}: {e}")
        conn.rollback()

def __stage_chrome_options():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--disable-features=PermissionsPolicyFeatures")
    return chrome_options

def generate_random_cookie():
    name = ''.join(random.choices('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789', k=random.randint(5, 10)))
    value = ''.join(random.choices("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", k=random.randint(10, 20)))
    return f'{name}={value}'

def stage_proxy(file_path):
    def read_proxy_file(file_path):
        with open(file_path, 'r') as file:
            line = file.readline().strip()
            proxy_host, proxy_port, proxy_username, proxy_password = line.split(':')
        return proxy_host, proxy_port, proxy_username, proxy_password

    proxy_host, proxy_port, proxy_username, proxy_password = read_proxy_file(file_path)

    proxy_options = {
        'proxy': {
            'http': f'http://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'https': f'https://{proxy_username}:{proxy_password}@{proxy_host}:{proxy_port}',
            'no_proxy': 'localhost,127.0.0.1'
        }
    }

    return proxy_options

def initialize_driver(proxy_options, user_agent):
    retries = 3
    for attempt in range(retries):
        try:
            chrome_options = __stage_chrome_options()
            seleniumwire_options = {
                'proxy': proxy_options,
                'ca_cert': '/usr/local/share/ca-certificates/ca.crt'
            }
            driver = seleniumwire_webdriver.Chrome(options=chrome_options, seleniumwire_options=seleniumwire_options)
            driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": user_agent})
            return driver
        except WebDriverException as we:
            print(f"Attempt {attempt + 1} of {retries} failed: {we}")
            if attempt == retries - 1:
                raise
            time.sleep(5)

def process_username(username, download=False, verbose=True):
    driver = None
    try:
        # conn = connect_to_db()
        target_url = 'https://www.instagram.com/{}/'.format(username)

        file_path = "proxy.txt"
        proxy_options = stage_proxy(file_path)

        user_agents_file = "user_agents.txt"
        user_agent = choose_random_line_reservoir_sampling(user_agents_file)

        # user_agent = choose_random_row(conn, "user_agent", "useragents")
        # user_agent from database
        # user_agent = sanitize_user_agent(user_agent[0])
        user_agent = sanitize_user_agent(user_agent)

        driver = initialize_driver(proxy_options, user_agent)

        cookies = [generate_random_cookie() for _ in range(random.randint(3, 7))]
        random_cookie_header = '; '.join(cookies)

        accepts_file = "accepts.txt"
        random_accept = choose_random_line_reservoir_sampling(accepts_file)

        referers_file = "referers.txt"
        random_referer = choose_random_line_reservoir_sampling(referers_file)

        driver.header_overrides = {
            'Cookie': random_cookie_header,
            'Accept': random_accept,
            'Referer': random_referer
        }

        driver.get(target_url)
        time.sleep(20)

        profile_pic_regex_pattern = re.compile(
            fr'<img alt="{username}\'s profile picture" class="[^"]*" crossorigin="[^"]*" draggable="[^"]*" src="([^"]*)"')
        post_regex_pattern = r'{}/p/([a-zA-Z0-9_-]+)/'.format(username)

        login_regex_pattern = re.compile(r'Log in')
        not_available_regex_pattern = re.compile(r"Sorry, this page isn't available.")

        if login_regex_pattern.search(driver.page_source):
            print(f"{username} : Log in encountered")
            return

        if not_available_regex_pattern.search(driver.page_source):
            print(f"{username} does not exist")
            return

        profile_pic_src_url = profile_pic_regex_pattern.search(driver.page_source)
        profile_pic_url = None
        if profile_pic_src_url:
            profile_pic_url = profile_pic_src_url.group(1).replace(';', '&')
        else:
            print(f"{username}'s profile picture not found. (Request denied)")
            return

        matches = re.findall(post_regex_pattern, driver.page_source)
        formatted_href_url = ["https://www.instagram.com/p/{}/media/?size=l".format(match) for match in matches]

        working_urls = []
        for href_url in formatted_href_url:
            driver.get(href_url)
            urls = re.findall(r'(https?://\S+)', driver.page_source)
            for url in urls:
                working_url = url.replace(';', '&')
                working_urls.append(working_url)

        if download:
            for index, url in enumerate(working_urls, start=1):
                save_path = os.path.join(f"{username}_images", f"image_{index}.jpg")
                download_image(url, save_path)
        else:
            with open('scraped_data.txt', 'a') as file:
                for index, url in enumerate(working_urls, start=1):
                    file.write(f"{username}:\"image_{index}\"=\"{url}\"\n")

        profile_pic_path = os.path.join(f"{username}_images", f"profile_picture.jpg")

        if download:
            download_image(profile_pic_url, profile_pic_path)
        else:
            with open('scraped_data.txt', 'a') as file:
                file.write(f"{username}:\"profile_pic\"=\"{profile_pic_url}\"\n")

        # update_user_data(conn, username, profile_pic_url, working_urls)

    except WebDriverException as we:
        print(f"A WebDriverException occurred while processing {username}. (Invalid Proxy?)")
        if verbose:
            print(f"{we}")
            traceback.print_exc()
    except Exception as e:
        print(f"An error occurred while processing {username}.")
        if verbose:
            print(f"{e}")
            traceback.print_exc()
    finally:
        if driver:
            driver.quit()

