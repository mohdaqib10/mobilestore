import re
from django.utils import timezone

from rest_framework.validators import ValidationError


def get_current_time():
    return timezone.now()


def get_delta_time(days):
    return get_current_time() + timezone.timedelta(days=days)


def validate_mobile(value):
    match = re.match(r'[6789]\d{9}$', value)
    if not match:
        raise ValidationError({'mobile': ['Enter a valid mobile number']})


def validate_required_field(request, key):
    if not (key in request.data and request.data[key]):
        raise ValidationError({key: ['This field is required']})


def create_instance(serializer_class, data):
    s = serializer_class(data=data)
    s.is_valid(raise_exception=True)
    s.save()
    return s.instance


def update_instance(instance, serializer_class, data):
    s = serializer_class(instance, data=data, partial=True)
    s.is_valid(raise_exception=True)
    s.save()
    return s.instance
