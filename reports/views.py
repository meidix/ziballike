from django.shortcuts import render
from django.views import View
from .utils import Request, Response, PipeLine, Jmonths
from ziballike import db
from bson import ObjectId

import jdatetime
from datetime import timedelta, date

class ReportAPIView(View):

    def get(self, request, *args, **kwargs):
        req = Request(request)
        pipeline = self.generate_query(req.params)
        transactions = db.get_collection('transaction')
        query = transactions.aggregate(pipeline)
        results = []
        for item in query:
            results.append(self.transform_key(item, req.params['mode']))
        res = Response(results)
        return res.to_json_response()

    def transform_key(self, item, mode):
        key = item['key']
        if mode == 'daily':
            item.update({
                'key': jdatetime.date.fromgregorian(**key).strftime("%Y/%m/%d")
            })
            return item
        elif mode == 'monthly':
            jdate = jdatetime.date.fromgregorian(**key, day=1)
            item.update({
                'key': f'{Jmonths.choices[jdate.month - 1][0]} {jdate.year}'
            })
            return item
        elif mode == 'weekly':
            real_date = date(year=key['year'], month=1, day=1) + timedelta(weeks=key['week'])
            jdate = jdatetime.date.fromgregorian(date=real_date)
            item.update({
                'key': f"هفته {int(jdate.strftime('%W')) + 1} سال {jdate.year}"
            })
            return item


    def generate_query(self, body):
        pipe = PipeLine()
        if 'merchantId' in body:
            pipe = pipe.match({ 'merchantId': ObjectId(body['merchantId'])})

        # convert dateitme to date
        pipe = pipe.project({
            'date': {
                'year': {"$year": "$createdAt"},
                'month': { "$month": "$createdAt"},
                'week' : { "$week": "$createdAt"},
                'day': { "$dayOfMonth": "$createdAt" }
            },
            'merchantId': "$merchantId",
            'amount': "$amount"
        })

        if body['mode'] == 'daily':
            pipe = pipe.group({
                '_id': {'year': "$date.year", 'month': "$date.month", 'day': "$date.day"},
                'count': { "$sum": 1 if body['type'] == 'count' else "$amount"},
                })
        elif body['mode'] == 'monthly':
            pipe = pipe.group({
                '_id': {'year': "$date.year", 'month': "$date.month"},
                'count': { "$sum": 1 if body['type'] == 'count' else "$amount"},
                })

        elif body['mode'] == 'weekly':
            pipe = pipe.group({
                '_id': {'year': "$date.year", 'week': "$date.week"},
                'count': { "$sum": 1 if body['type'] == 'count' else "$amount"},

                }
            )

        return pipe.project({
             '_id': 0,
            'key': "$_id",
            'value': "$count"
        }).query_string