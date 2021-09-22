import json
import logging
import os

import requests

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
separator = "##"


def notify_map_share(notification_text):
    headers = {'User-Agent': 'Mozilla/5.0'}
    payload = {'deviceIds': '146527', 'fromAddr': os.environ['SENDER_NUMBER'], 'messageText': notification_text}

    session = requests.Session()
    session.post(
        'https://share.garmin.com/' + os.environ['MAP_SHARE_ID'] +'/Map/SendMessageToDevices',
        headers=headers,
        data=payload)


def get_aurora_forecast():
    response = requests.get('https://1a9or2as6g.execute-api.eu-central-1.amazonaws.com/Prod')
    data = json.loads(response.content)

    predictions = []
    for prediction in data['breakdown']:
        predictions.append(prediction['start'] + separator + prediction['kp']);

    predictions.sort()
    kp_days = ['', '', '']
    i = 0
    for prediction in predictions:
        kp_days[i // 8] += (prediction.split(separator)[1])
        i += 1

    logging.info(kp_days)
    return '-'.join(kp_days)


notify_map_share(get_aurora_forecast())
