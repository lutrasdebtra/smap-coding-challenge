import csv
import os
from datetime import datetime

import pytz
from consumption.models import *
from django.core.management.base import BaseCommand
from django.db.models import Avg, Sum
from django.utils.timezone import make_aware

import dashboard


class Command(BaseCommand):
    """ Imports data from CSV files into database. """
    help = 'import data'

    def add_arguments(self, parser):
        """ Adds file location and append flags to command. """
        data_dir = os.path.abspath(os.path.join(dashboard.__path__[0], "../../data"))
        # Named (optional) arguments.
        # Location of user_data.csv
        parser.add_argument(
            '--user_data',
            action='store',
            dest='user_data_loc',
            default=os.path.join(data_dir, "user_data.csv"),
            help="Location of 'user_data.csv'.",
        )
        # Location of consumption files.
        parser.add_argument(
            '--user_consumption',
            action='store',
            dest='user_consumption_loc',
            default=os.path.join(data_dir, "consumption"),
            help='Location of folder containing individual consumption data files.',
        )
        # Flag for whether or not old objects should be deleted (default).
        parser.add_argument(
            '--append',
            action='store_true',
            dest='append',
            help='Appends new imports instead of deleting them.',
        )

    def handle(self, *args, **options):
        """ Main method for command. """
        user_data_loc = options['user_data_loc']
        user_consumption_loc = options['user_consumption_loc']
        # Check arguments:
        if not os.path.isfile(user_data_loc):
            self.stdout.write("'{}' is not a valid file path.".format(user_data_loc))
            return
        if not os.path.exists(user_consumption_loc):
            self.stdout.write("'{}' is not a valid path.".format(user_consumption_loc))
            return

        # Delete objects if not appending.
        if not options['append']:
            self.rollback()

        user_data_objects = self.handle_user_data(user_data_loc)
        if user_data_objects:
            self.handle_consumption_data(user_consumption_loc, user_data_objects)
            self.create_time_point_aggregate_data()

            self.stdout.write("Import completed.")

    def handle_user_data(self, user_data_loc):
        """ Handled user_data.csv and UserData model. """
        expected_header = ['id', 'area', 'tariff']
        user_data_objects = {}

        with open(user_data_loc, newline='') as csvfile:
            reader = csv.reader(csvfile, delimiter=',', quotechar='|')
            # Check header is correct.
            header = next(reader)
            if header != expected_header:
                self.stdout.write("'{}' has a malformed header, the header must be: {}".format(
                    user_data_loc, ','.join(expected_header)))
                return user_data_objects
            for row in reader:
                if not UserData.objects.filter(id=row[0]).exists():
                    self.stdout.write(
                        "Creating UserData Object: id = {}, area = {}, tariff = {}".format(row[0], row[1], row[2]))
                    user_data_objects[row[0]] = UserData.objects.create(id=row[0], area=row[1], tariff=row[2])
                else:
                    user_data_objects[row[0]] = UserData.objects.get(id=row[0])
        return user_data_objects

    def handle_consumption_data(self, user_data_loc, user_data_objects):
        """ Handles all consumption csv files. """
        consumption_time_point_objects = []
        # Would be worth in a production version to find local timezone instead of hardcoding.
        time_zone = pytz.UTC
        # Gets a set of field values to avoid duplicate entries. Assumes users only have 1 datapoint per time point.
        existing_objects = set(ConsumptionTimePoint.objects.values_list('time_point', 'user_data').distinct())

        for filename in os.listdir(user_data_loc):
            if filename.endswith(".csv"):
                full_file_path = os.path.join(user_data_loc, filename)
                expected_header = ['datetime', 'consumption']
                user_data_id = filename.split(".")[0]
                if user_data_id in user_data_objects:
                    user_data_object = user_data_objects[user_data_id]
                else:
                    self.stdout.write(
                        "UserData object with id: {}, not found, skipping file: {}.".format(user_data_id, filename))
                    continue
                with open(full_file_path, newline='') as csvfile:
                    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
                    # Check header is correct.
                    header = next(reader)
                    if header != expected_header:
                        self.stdout.write("'{}' has a malformed header, the header must be: {}, skipping file.".format(
                            full_file_path, ','.join(expected_header)))
                        continue
                    for row in reader:
                        date_time_with_timezone = self.create_timezone_aware_datetime_from_string(row[0], time_zone)
                        # Checks if field tuple already exists.
                        if not (date_time_with_timezone, int(user_data_id)) in existing_objects:
                            consumption_time_point_objects.append(
                                ConsumptionTimePoint(time_point=date_time_with_timezone, consumption=row[1],
                                                     user_data=user_data_object))
                    self.stdout.write("Creating ConsumptionTimePoint Objects for UserData id = {}".format(user_data_id))
        self.stdout.write("Committing ConsumptionTimePoint Objects to database.")
        # Bulk create at end for speed.
        ConsumptionTimePoint.objects.bulk_create(consumption_time_point_objects)

    def create_time_point_aggregate_data(self):
        """ Creates average and total information for each distinct time point. """
        # Regardless of whether --append is used, these values should be recalcuated.
        TimePointAggregateData.objects.all().delete()
        self.stdout.write("Creating TimePointAggregateData values.")
        data = ConsumptionTimePoint.objects.values('time_point').annotate(total=Sum('consumption'),
                                                                          average=Avg('consumption'))
        self.stdout.write("Committing TimePointAggregateData Objects to database.")
        TimePointAggregateData.objects.bulk_create([TimePointAggregateData(**q) for q in data])

    def rollback(self):
        """ Removes objects from all tables. """
        self.stdout.write("Deleting previously imported objects.")
        UserData.objects.all().delete()
        ConsumptionTimePoint.objects.all().delete()
        TimePointAggregateData.objects.all().delete()

    @staticmethod
    def create_timezone_aware_datetime_from_string(date_string, time_zone):
        """ Creates a datetime object from a string, and adds timezone information. """
        date_time_without_timezone = datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        date_time_with_timezone = make_aware(date_time_without_timezone, timezone=time_zone)
        return date_time_with_timezone
