# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.shortcuts import render

from .models import *


# Create your views here.


def summary(request):
    data = json.dumps(
        [[str(x[0]), x[1]] for x in TimePointAggregateData.objects.values_list('time_point', 'average')[::48]])
    context = {
        'message': 'Hello!',
        'time_point_aggregate_data': data
    }
    return render(request, 'consumption/summary.html', context)


def detail(request):
    context = {
    }
    return render(request, 'consumption/detail.html', context)
