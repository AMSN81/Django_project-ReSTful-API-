from django.core.validators import BaseValidator
from django.utils.deconstruct import deconstructible
from django.utils.translation import ngettext_lazy,gettext_lazy as _
from django.core.exceptions import ValidationError


@deconstructible
class customValidator(BaseValidator):
    message = _('Length of number should be %(limit_value)s.')
    code = 'value'

    def compare(self, a, b):
        return len(a) != b

def validate_phone_number(value):
    if (value[0:2] == '09') and (len(value) == 11):
        return value
    else:
        raise ValidationError("Please Enter a valid phone number")

