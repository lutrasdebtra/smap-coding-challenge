from django.db import models


class UserData(models.Model):
    """ Holds basic user data. """
    id = models.IntegerField(primary_key=True, editable=False)  # id is taken from data.
    area = models.CharField(max_length=20)
    tariff = models.CharField(max_length=20)


class ConsumptionTimePoint(models.Model):
    """ Individual consumption time points with a One-to-Many relationship with UserData """
    time_point = models.DateTimeField()
    consumption = models.FloatField()
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE)


class TimePointAggregateData(models.Model):
    """ Holds totals and averages for user consumption across individual time points. """
    time_point = models.DateTimeField()
    average = models.FloatField()
    total = models.FloatField()
