from datetime import timedelta
from re import match

from django.core import exceptions
from django.db.models import fields
from django.db import models
from django.utils.translation import ugettext_lazy as _

class TimedeltaIntegerField(fields.IntegerField):
    def get_db_prep_value(self, value):
        if value is None:
            return None
        return value.days * 86400 + value.seconds

    def to_python(self, value):
        if value is None:
            return value
        try:
            return timedelta(seconds=value)
        except (TypeError, ValueError):
            raise exceptions.ValidationError("This value must be a an integer representing a timedelta.")

class TimedeltaField(models.Field):

    __metaclass__ = models.SubfieldBase

    def __init__(self, *args, **kwargs):
        super(TimedeltaField, self).__init__(*args, **kwargs)

    def get_internal_type(self):
        return "IntegerField"

    def to_python(self, value):
        if value is None:
            return timedelta(0)
        if isinstance(value, timedelta):
            return value
        try:
            return timedelta(seconds=int(value))
        except (TypeError, ValueError):
            pass
        if isinstance(value, unicode):
            #example '34722 days, 5:20:00.0000'
            m = match(r"((?P<days>-?\d+) days?, )?(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)(\.(?P<milliseconds>\d+))?", value)
            if not m:
                raise exceptions.ValidationError("This value must a string in the form of '34722 days, 5:20:00.0000' and not this '%s'"%(value,))
            else:
                return timedelta(
                    days = int(m.group('days')) if m.group('days') else 0,
                    hours = int(m.group('hours')),
                    minutes = int (m.group('minutes')),
                    seconds = int (m.group('seconds')),
                    milliseconds = int(m.group('milliseconds')) if m.group('milliseconds') else 0,
                    )
            
    def get_db_prep_value(self, value):
        return value.days * 86400 + value.seconds
