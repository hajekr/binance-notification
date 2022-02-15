import json
import logging
import os

import requests
from twilio.rest import Client

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.INFO)
separator = "##"


def notify_twilio(notification_text):
    client = Client(os.environ['TWILIO_ACCOUNT_SID'], os.environ['TWILIO_AUTH_TOKEN'])

    message = client.messages.create(
        body=notification_text,
        from_=os.environ['SENDER_NUMBER'],
        to=os.environ['RECIPIENT_NUMBER']
    )

    logging.info('sent ' + message.sid)


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


notify_twilio(get_aurora_forecast())
