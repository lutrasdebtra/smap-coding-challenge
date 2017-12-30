# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import Http404
from django.shortcuts import render

from .models import *


def summary(request):
    """ View for a summary of consumption data. """

    # Gets every 12pm TimePointAggregateData object. Also converts it into a format readable by Charts.js
    # Before converting to JSON.
    aggregate_data = json.dumps([[str(x[0]), x[1]] for x in
                                 TimePointAggregateData.objects.values_list('time_point', 'average')[25::48]])
    context = {
        'time_point_aggregate_data': aggregate_data,
        'user_data': UserData.objects.all(),
        'page': 'Summary Page'
    }
    return render(request, 'consumption/summary.html', context)


def detail(request, pk):
    """ View for a single user. """
    try:
        user = UserData.objects.get(pk=pk)
        time_points_non_json = user.consumptiontimepoint_set.all()
        # Gets every 12pm ConsumptionTimePoint object. Also converts it into a format readable by Charts.js
        # Before converting to JSON.
        time_points = json.dumps([[str(x[0]), x[1]] for x in
                                  time_points_non_json.values_list(
                                                 'time_point', 'consumption')[25::48]])
        # Also gets a

    except UserData.DoesNotExist:
        raise Http404
    context = {
        'user_data': user,
        'time_points': time_points,
        'time_points_non_json': time_points_non_json,
        'page': 'User {} Detail Page'.format(user.id)

    }
    return render(request, 'consumption/detail.html', context)
