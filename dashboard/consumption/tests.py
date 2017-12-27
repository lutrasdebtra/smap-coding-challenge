from datetime import datetime

from django.test import TestCase

from .models import *


class Tests(TestCase):
    def test_basic_model_creation(self):
        """ Tests model association loading. """
        user_data_object = UserData.objects.create(id=1, area="a1", tariff="t1")
        user_data_object.save()
        consumption_time_point_object = ConsumptionTimePoint.objects.create(time_point=datetime.now(),
                                                                            consumption=20.0,
                                                                            user_data=user_data_object)
        consumption_time_point_object.save()
        self.assertIsNotNone(consumption_time_point_object.user_data)
        self.assertEquals(1, len(user_data_object.consumptiontimepoint_set.all()))
