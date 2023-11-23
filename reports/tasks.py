from ziballike import db
from .utils import PipeLine
from bson import ObjectId
from bson.json_utils import dumps
from django.utils import timezone
from datetime import datetime, timedelta
from django.conf import setting
import jdatetime
import requests

def summarize_and_notify():
    transaction = db.get_collection('transaction')
    merchants = transaction.distict("merchantId")
    yesterday = timezone.now().date() - timedelta(days=1)

    for merchant in merchants:
        query =get_query(merchant, yesterday)
        result = transaction.aggregate(query)
        send_notification(merchant, result, yesterday)


def get_query(merchantId, date):
    start_date = datetime.combine(date, datetime.min.time())
    end_date = datetime.combine(date, datetime.max.time())
    pipe = PipeLine()
    return pipe.match({
        'merchantId': ObjectId(merchantId),
        'createdAt': {
            '$gte': start_date,
            '$lt': end_date
        }
    }).project({
        'date': {
            'year': {"$year": "$createdAt"},
            'month': { "$month": "$createdAt"},
            'week' : { "$week": "$createdAt"},
            'day': { "$dayOfMonth": "$createdAt" }
        },
        'merchantId': "$merchantId",
        'amount': "$amount"
    }).group({
        '_id': {'year': "$date.year", 'month': "$date.month", 'day': "$date.day"},
        'count': { "$sum": 1 },
        'amount': { "$sum": "$amount"}
    }).project({
        '_id': 0,
        'count': 1,
        'amount': 1
    }).query_string

def send_notification(merchant, result, date):
    serialized = dumps(result)
    payload = {
        'medium': 'sms',
        'payload': {
            'receiver': merchant,
            'messege': serialized
        }
    }
    url = settings.get('NOTIFICATION_SERVICE_URL')
    perform_request(url, payload)

    payload['medium'] = 'email'
    payload['payload']['subject'] = f'transactions of {jdatetime.date.fromgregorian(date)}'
    perform_request(url, payload)


def perform_request(url, payload):
    response = requests.post(
        url,
        payload,
        headers={'Content-Type': "application/json"})
    if response.status_code != 200:
        raise Exception("An error occured")
