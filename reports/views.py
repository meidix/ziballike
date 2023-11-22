from django.shortcuts import render
from django.views import View
from django.core.exceptions import ValidationError
from .utils import Request, Response, PipeLine, Jmonths
from .validators import *
from ziballike import db
from bson import ObjectId
from bson.errors import InvalidId

import jdatetime
from datetime import timedelta, date

class BaseReportAPIView(View):
    collection = None


    def get(self, request, *args, **kwargs):
        try:
            req = Request(request, [validate_mode, validate_type])
            pipeline = self.generate_query(req.params)
            query = self.collection.aggregate(pipeline)
            results = [self.transform_key(item, req.params['mode']) for item in query]
            res = Response(results, 200)
            return res.to_json_response()
        except ValidationError as err:
            data = {
             'type': 'ValidationError',
             'errorCode': err.code,
             'errMsg': err.message
            }
            res = Response(data, 400)
            return res.to_json_response()
        except InvalidId:
            data = {
                'type': "Invalid ObjectId"
            }
            res = Response(data, 400)
            return res.to_json_response()
        except:
            data = {
                "error": "An Internal Server Error occured"
            }
            res = Response(data, 500)
            return res.to_json_response()

    def generate_query(self, body):
        pass

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


class ReportAPIView(BaseReportAPIView):

    collection = db.get_collection('transaction')

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


class ReportCacheAPIView(BaseReportAPIView):
    collection = db.get_collection('transaction_summary')

    def generate_query(self, body):
        pipe = PipeLine()
        if 'merchantId' in body:
            pipe = pipe.match({ '_id.merchantId': ObjectId(body['merchantId'])})

        if body['mode'] == 'monthly':
            pipe =  pipe.group({
                '_id': {
                    'year': '$_id.year',
                    'month': '$_id.month'
                },
                'value': { "$sum": "$monthlyCount" if body['type'] == 'count' else "$monthlyAmount"}
            })

        elif body['mode'] == 'daily':
            pipe = pipe.unwind("$weeklySummaries").unwind("$weeklySummaries.dailySummaries").group({
                '_id': {
                    'year': "$_id.year",
                    'month': "$_id.month",
                    'day': "$weeklySummaries.dailySummaries.day"
                },
                'value': { "$sum": f"$weeklySummaries.dailySummaries.{body['type']}" }
            })

        elif body['mode'] == 'weekly':
            pipe = pipe.unwind("$weeklySummaries").group({
                '_id': {
                    'year': "$_id.year",
                    'week': "$weeklySummaries.week"
                },
                'value' : { "$sum": f"$weeklySummaries.{body['type']}"}
            })

        return pipe.project({
            '_id': 0,
            'key': "$_id",
            'value': 1
        }).query_string