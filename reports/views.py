from django.shortcuts import render
from django.views import View
from .utils import Request, Response
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

    def generate_query(self, body: dict):
        # query_string = []
        # merchant_filter = { "$match" : {"merchantId": None}}
        # if 'merchantId' in body:
        #     merchant_filter['$match']['merchantId'] = ObjectId(body["merchantId"])
        #     query_string.append(merchant_filter)

        query_string =  [{ "$match" : {"merchantId": ObjectId(body['merchantId'])}},
        { "$project": {
            'date': {
                "$dateToString": {
                    'format': "%Y-%m-%d",
                    'date': "$createdAt"
                }
            },
            'merchantId': "$merchantId"
        }},
        { "$group": {
                '_id': "$date",
                'count': { "$sum": 1},

            }
        },
        { "$project": {
            "_id": 0,
            'key': "$_id",
            'value': "$count"

        }}
        ]
        return query_string