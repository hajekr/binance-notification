import logging
import os

import psycopg2
import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
db_connection = psycopg2.connect(os.environ.get("DATABASE_URL"))


def create_table_if_not_exists():
    cursor = db_connection.cursor()
    cursor.execute('CREATE TABLE IF NOT EXISTS listings(id SERIAL PRIMARY KEY, url CHAR(255) NOT NULL, title CHAR(255) NOT NULL);')
    logging.info('Table created successfully')
    db_connection.commit()


def notify_slack(notification_text):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    channel_id = os.environ.get("CHANNEL_ID")

    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text=notification_text
        )
        logging.info(result)

    except SlackApiError as e:
        logging.error(e)


def notify_listing(relative_url):
    absolute_url = 'https://www.binance.com' + relative_url;
    logging.info('Page url ' + absolute_url)

    listing_detail_page = requests.get(absolute_url)
    soup = BeautifulSoup(listing_detail_page.content, 'html.parser')

    page_header = soup.find("h1", {"class": "css-kxziuu"}).contents[0]
    logging.info('Page header ' + page_header)

    cursor = db_connection.cursor()
    cursor.execute('SELECT url FROM listings WHERE url = \'' + absolute_url + '\'')
    data = cursor.fetchall()

    if len(data) == 0:
        message = '*' + page_header + '* \n' + absolute_url

        logging.info('Action: NOTIFY')
        notify_slack(message)

        cursor.execute('INSERT INTO listings(url, title) VALUES (\'' + absolute_url + '\',\'' + page_header + '\')')
    else:
        logging.info('Action: SKIP')

    db_connection.commit()
    logging.info(' --- ')


def notify_new_listings():
    page = requests.get('https://www.binance.com/en/support/announcement/c-48?navId=48')
    soup = BeautifulSoup(page.content, 'html.parser')

    # find links by class of all links in "New Crypto Listings" section
    new_listings = soup.find_all("a", {"class": "css-1ej4hfo"})
    for listing in new_listings:
        notify_listing(listing['href'])


create_table_if_not_exists()
notify_new_listings()

db_connection.close()
