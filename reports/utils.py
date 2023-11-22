from django.http import JsonResponse, HttpResponse, HttpRequest
from bson.json_util import dumps
from django.db.models import TextChoices

class Request:
    def __init__(self, request: HttpRequest, validators=[]):
        self.request = request
        self._initial_params = eval(request.body.decode("UTF-8"))
        self.validators = validators
        self.validate()

    def validate(self):
        for validator in self.validators:
            validator(self._initial_params)
        self.params = self._initial_params

    def get_param(self, param_name, default=None):
        return self.params.get(param_name, default)



class Response:
    def __init__(self, data=None, status=200):
        self.data = data
        self.status = status

    def to_json_response(self):
        return HttpResponse(dumps(self.data), content_type="application/json", status=self.status)


class PipeLine:

    def __init__(self):
        self.query_string = []

    def __repr__(self) -> str:
        self.query_string

    def match(self, expr):
        self._add_process("$match", expr)
        return self

    def group(self, expr):
        self._add_process("$group", expr)
        return self

    def project(self, expr):
        self._add_process("$project", expr)
        return self

    def _add_process(self, process_name, expr):
        self.query_string.append(
            {process_name: expr}
        )

    def out(self, collection_name):
        self._add_process('$out', collection_name)
        return self

    def unwind(self, array):
        self._add_process("$unwind", array)
        return self


class Jmonths(TextChoices):
    FARVARDIN = 'فروردین'
    ORDIBEHESHT = 'اردیبهشت'
    KHORDAD = 'خرداد'
    TIR = 'تیر'
    MORDAD = 'مرداد'
    SHAHRIVAR = 'شهریور'
    MEHR = 'مهر'
    ABAN = 'آبان'
    AZAR = 'آذر'
    DEY = 'دی'
    BAHMAN = 'بهمن'
    ESFAND = 'اسفند'