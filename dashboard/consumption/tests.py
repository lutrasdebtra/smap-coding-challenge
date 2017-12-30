import os
from datetime import datetime

import pytz
from django.core.management import call_command
from django.test import TestCase
from django.utils.six import StringIO
from django.utils.timezone import make_aware

import dashboard
from .models import *


class Tests(TestCase):
    def test_basic_model_creation(self):
        """ Tests model association loading. """
        user_data_object = UserData.objects.create(id=1, area="a1", tariff="t1")
        user_data_object.save()
        consumption_time_point_object = ConsumptionTimePoint.objects.create(time_point=make_aware(datetime.now(),
                                                                                                  pytz.UTC),
                                                                            consumption=20.0,
                                                                            user_data=user_data_object)
        consumption_time_point_object.save()
        TimePointAggregateData.objects.create(time_point=make_aware(datetime.now(), pytz.UTC), total=0.0, average=0.0)

        self.assertIsNotNone(consumption_time_point_object.user_data)
        self.assertEquals(1, user_data_object.consumptiontimepoint_set.all().count())
        self.assertEquals(1, UserData.objects.all().count())
        self.assertEquals(1, ConsumptionTimePoint.objects.all().count())
        self.assertEquals(1, TimePointAggregateData.objects.all().count())


class ImportTests(TestCase):
    def setUp(self):
        self.data_dir = os.path.abspath(os.path.join(dashboard.__path__[0], "../../test_data"))
        self.out = StringIO()
        self.args = []
        self.options = {'user_data_loc': os.path.join(self.data_dir, "user_data.csv"),
                        'user_consumption_loc': os.path.join(self.data_dir, "consumption")}

    def test_import_function_and_append(self):
        """ Check basic import functioning. """
        self.out.flush()
        call_command('import', *self.args, **self.options, stdout=self.out)

        self.assertEquals(UserData.objects.all().count(), 3)
        self.assertEquals(ConsumptionTimePoint.objects.all().count(), 9)
        self.assertEquals(TimePointAggregateData.objects.all().count(), 3)
        self.assertIn("Import completed.", self.out.getvalue())

        """ Check append a doesn't add additional objects that already exist. """
        self.out.flush()
        self.options['append'] = True

        call_command('import', *self.args, **self.options, stdout=self.out)

        self.assertEquals(UserData.objects.all().count(), 3)
        self.assertEquals(ConsumptionTimePoint.objects.all().count(), 9)
        self.assertEquals(TimePointAggregateData.objects.all().count(), 3)
        self.assertIn("Import completed.", self.out.getvalue())

    def test_import_invalid_file_path(self):
        """ Check invalid filepath. """
        self.out.flush()
        options = {'user_data_loc': os.path.join(self.data_dir, "user_data567.csv"),
                   'user_consumption_loc': os.path.join(self.data_dir, "consumption")}
        call_command('import', *self.args, **options, stdout=self.out)
        self.assertIn("is not a valid file path.", self.out.getvalue())

    def test_malformed_header(self):
        """ Checks a malformed header. """
        self.out.flush()
        options = {'user_data_loc': os.path.join(self.data_dir, "user_data_fail.csv"),
                   'user_consumption_loc': os.path.join(self.data_dir, "consumption")}
        call_command('import', *self.args, **options, stdout=self.out)
        self.assertIn("malformed header", self.out.getvalue())
