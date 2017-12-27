from django.db import models


class UserData(models.Model):
    """ Holds basic user data. """
    id = models.IntegerField(primary_key=True, editable=False)  # id is taken from data.
    area = models.CharField(max_length=20)
    tariff = models.CharField(max_length=20)
