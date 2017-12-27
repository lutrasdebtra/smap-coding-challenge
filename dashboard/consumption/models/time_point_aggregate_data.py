from django.db import models


class TimePointAggregateData(models.Model):
    """ Holds totals and averages for user consumption across individual time points. """
    time_point = models.DateTimeField()
    average = models.FloatField()
    total = models.FloatField()
