from django.shortcuts import render
from django.views import View
from .utils import Request, Response, PipeLine
from ziballike import db
from bson import ObjectId
# from jdatetime import jdatetime

class ReportAPIView(View):

    def get(self, request, *args, **kwargs):
        req = Request(request)
        pipeline = self.generate_query(req.params)
        transactions = db.get_collection('transaction')
        query = transactions.aggregate(pipeline)
        # for item in query:
        #     item['key'] = jdatetime.fromgregorian(item['key'])
        res = Response(list(query))
        return res.to_json_response()



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
            'merchantId': "$merchantId"
        })

        if body['mode'] == 'daily':
            pipe = pipe.group({
                '_id': ["$date.year", "$date.month", "$date.day"],
                'count': { "$sum": 1},
                })
        elif body['mode'] == 'monthly':
            pipe = pipe.group({
                '_id': ["$date.year", "$date.month"],
                'count': { "$sum": 1},

                })

        elif body['mode'] == 'weekly':
            pipe = pipe.group({
                '_id': ["$date.year", "$date.week"],
                'count': { "$sum": 1},

                }
            )

        return pipe.project({
             '_id': 0,
            'key': "$_id",
            'value': "$count"
        }).query_string