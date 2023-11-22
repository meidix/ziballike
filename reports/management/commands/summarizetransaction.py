from typing import Any, Optional
from django.core.management.base import BaseCommand, CommandError, CommandParser
from reports.utils import PipeLine
from ziballike import db
from bson import ObjectId


class Command(BaseCommand):
    help = "Computes the summary of transactions and saves it to a collection for further use"

    def add_arguments(self, parser: CommandParser) -> None:
        return super().add_arguments(parser)

    def handle(self, *args: Any, **options: Any) -> str | None:
        query = self.generate_query()
        self.stdout.write("Accessing the transaction collection")
        transactions = db.get_collection('transaction')
        self.stdout.write("Summarizing")
        transactions.aggregate(query)
        self.stdout.write("SUCCESS")


    def generate_query(self):
        pipe = PipeLine()
        return pipe.group({
            '_id': {
                'merchantId': "$merchantId",
                'year': { "$year" : "$createdAt"},
                'month': { "$month" : "$createdAt"},
                'week': { "$week": "$createdAt"},
                'day': { "$dayOfMonth": "$createdAt"}
            },
            'dailyCount': { "$sum": 1},
            'dailyAmount': { "$sum": "$amount"}
        }).group({
            '_id': {
                'merchantId': "$_id.merchantId",
                'year': "$_id.year",
                'month': '$_id.month',
                'week': '$_id.week'
            },
            'weeklyCount': { '$sum': '$dailyCount'},
            'weeklyAmount': { "$sum": "$dailyAmount"},
            'dailySummaries': {
                "$push": {
                    'day': "$_id.day",
                    'count': '$dailyCount',
                    'amount': '$dailyAmount'
                }
            }
        }).group({
            '_id': {
                'merchantId': "$_id.merchantId",
                'year': "$_id.year",
                'month': '$_id.month',
            },
            'monthlyCount' : { "$sum": "$weeklyCount"},
            'monthlyAmount': { "$sum": "$weeklyAmount"},
            'weeklySummaries': {
                "$push": {
                    "week": "$_id.week",
                    'count': '$weeklyCount',
                    'amount': '$weeklyAmount',
                    'dailySummaries': "$dailySummaries"
                }
            }
        }).out('transaction_summary').query_string
