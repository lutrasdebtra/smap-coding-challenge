from django.db import models

from .user_data import UserData


class ConsumptionTimePoint(models.Model):
    """ Individual consumption time points with a One-to-Many relationship with UserData """
    date_time = models.DateTimeField()
    consumption = models.FloatField()
    user_data = models.ForeignKey(UserData, on_delete=models.CASCADE)  # One-to-Many with UserData (Many side).
