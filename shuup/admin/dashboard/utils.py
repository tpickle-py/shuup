import datetime
import time
from heapq import heappop, heappush
from itertools import islice

from django.utils.timezone import now

from shuup.admin.module_registry import get_modules


def get_activity(request, n_entries=30, cutoff_hours=10):
    """
    Get Activity objects from all modules as a list in latest-first order.

    :param request: Request context
    :type request: django.http.request.HttpRequest
    :param n_entries: Number of entries to return in total.
    :type n_entries: int
    :param cutoff_hours: Calculate cutoff datetime so the oldest entry should be at most this old
    :type cutoff_hours: float
    :return: List of Activity objects
    :rtype: list[Activity]
    """

    cutoff_dt = now() - datetime.timedelta(hours=cutoff_hours)
    activities = []
    for module in get_modules():
        for activity in islice(module.get_activity(request, cutoff=cutoff_dt), n_entries):
            heappush(activities, (-time.mktime(activity.datetime.timetuple()), activity))
    out = []
    while activities and len(out) < n_entries:
        out.append(heappop(activities)[1])
    return out
