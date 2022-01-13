import logging
import os

import psycopg2
import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
db_connection = psycopg2.connect(os.environ.get("DATABASE_URL"))


def create_table_if_not_exists():
    cursor = db_connection.cursor()
    cursor.execute(
        'CREATE TABLE IF NOT EXISTS listings(id SERIAL PRIMARY KEY, url CHAR(255) NOT NULL, title CHAR(255) NOT NULL);')
    logging.info('Table created successfully')
    db_connection.commit()


def notify_slack(notification_text):
    client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))
    channel_id = os.environ.get("CHANNEL_ID")

    try:
        result = client.chat_postMessage(
            channel=channel_id,
            text=notification_text,
            unfurl_links=False,
            unfurl_media=False
        )
        logging.info(result)

    except SlackApiError as e:
        logging.error(e)


def is_allowed(text):
    return not ('Trading Pairs' in text or 'Isolated Margin' in text or 'Futures' in text)


def get_prefix(title):
    if 'Launchpad' in title or 'Launchpool' in title:
        return ':vibe: :rocket: '
    else:
        return ''


def notify_listing(code, title):
    absolute_url = 'https://www.binance.com/en/support/announcement/' + code
    logging.info('Page url ' + absolute_url)
    logging.info('Page title ' + title)

    cursor = db_connection.cursor()
    cursor.execute('SELECT url FROM listings WHERE url like trim(\'' + absolute_url + '\')')
    data = cursor.fetchall()

    if len(data) == 0:
        if is_allowed(title):
            logging.info('Action: NOTIFY')
            message = get_prefix(title) + '*' + title + '* \n' + absolute_url
            notify_slack(message)
        else:
            logging.info('Action: SKIP - content not allowed')

        cursor.execute(
            'INSERT INTO listings(url, title) VALUES (trim(\'' + absolute_url + '\'),trim(\'' + title + '\'))')
    else:
        logging.info('Action: SKIP - already notified')

    db_connection.commit()
    logging.info(' --- ')


def notify_new_listings():
    query = {'type': '1', 'pageNo': '1', 'pageSize': '5', 'catalogId': '48'}
    response = requests.get('https://www.binance.com/bapi/composite/v1/public/cms/article/list/query', params=query)
    articles = response.json().get('data').get('catalogs')[0].get('articles')

    for article in articles:
        notify_listing(article.get('code'), article.get('title'))


create_table_if_not_exists()
notify_new_listings()

db_connection.close()
