import logging
import os
from _datetime import datetime
from _datetime import timedelta
from _datetime import timezone

import pytz
import requests
from bs4 import BeautifulSoup
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)


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

    listing_detail_page = requests.get(absolute_url)
    soup = BeautifulSoup(listing_detail_page.content, 'html.parser')

    page_header = soup.find("div", {"class": "css-kxziuu"}).contents[0]
    publication_time_string = soup.find("div", {"class": "css-17s7mnd"}).contents[0]

    publication_time = datetime.strptime(publication_time_string, '%Y-%m-%d %H:%M').replace(tzinfo=pytz.UTC)
    previous_run_time = datetime.now(timezone.utc) - timedelta(hours=0, minutes=12)

    if publication_time > previous_run_time:
        message = '*' + page_header + '* \n' + absolute_url

        logging.info('Notify ' + message)
        notify_slack(message)
    else:
        logging.info('Skipping message from ' + publication_time_string)


def notify_new_listings():
    page = requests.get('https://www.binance.com/en/support/announcement/c-48?navId=48')
    soup = BeautifulSoup(page.content, 'html.parser')

    # find links by class of all links in "New Crypto Listings" section
    new_listings = soup.find_all("a", {"class": "css-1ej4hfo"})
    for listing in new_listings:
        notify_listing(listing['href'])


notify_new_listings()
