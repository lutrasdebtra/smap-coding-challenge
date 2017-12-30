# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import json

from django.http import Http404
from django.shortcuts import render

from .models import *


# Create your views here.


def summary(request):
    aggregate_data = json.dumps([[str(x[0]), x[1]] for x in
                                 TimePointAggregateData.objects.values_list('time_point', 'average')[25::48]])
    context = {
        'message': 'Hello!',
        'time_point_aggregate_data': aggregate_data,
        'user_data': UserData.objects.all()
    }
    return render(request, 'consumption/summary.html', context)


def detail(request, pk):
    context = {}
    try:
        context['user_data'] = UserData.objects.get(pk=pk)
        context['time_points'] = json.dumps([[str(x[0]), x[1]] for x in
                                             context['user_data'].consumptiontimepoint_set.all().values_list(
                                                 'time_point', 'consumption')[25::48]])
        context['time_points_non_json'] = context['user_data'].consumptiontimepoint_set.all()
    except UserData.DoesNotExist:
        raise Http404
    return render(request, 'consumption/detail.html', context)
