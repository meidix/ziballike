from django.core.exceptions import ValidationError

def validate_mode(data):
    if 'mode' not in data:
        raise ValidationError("You need to provide the mode in which you make query", "ModeAbsent")
    if data['mode'] not in ('monthly', 'weekly', 'daily'):
        raise ValidationError(f"The mode is either monthly, weekly or daily provided: {data['mode']}", "ModeInvalid")


def validate_type(data):
    if 'type' not in data:
        raise ValidationError("You need to provide the type in which you make query", "TypeAbsent")
    if data['type'] not in ('count', 'amount'):
        raise ValidationError(f"The type is either count or amount provided: {data['type']}", "TypeInvalid")