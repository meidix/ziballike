from django.http import JsonResponse, HttpResponse, HttpRequest
from bson.json_util import dumps

class Request:
    def __init__(self, request: HttpRequest):
        self.request = request
        self.params = eval(request.body.decode("UTF-8"))


    def get_param(self, param_name, default=None):
        return self.params.get(param_name, default)


class Response:
    def __init__(self, data=None, status=200):
        self.data = data
        self.status = status

    def to_json_response(self):
        return HttpResponse(dumps(self.data), content_type="application/json", status=self.status)