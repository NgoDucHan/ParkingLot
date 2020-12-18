# -*- coding: utf-8 -*-

import datetime
from pytz import timezone, UTC
from dateutil.relativedelta import relativedelta

from odoo import models


class ResourceCalendar(models.Model):
    _inherit = 'resource.calendar'

    def _in_work_time(self, dt, resource=None):
        """Return the boolean work interval boundary within the search range.
            if the dt in the range -> return True, else False.
        :param dt: reference datetime
        :rtype: datetime | None
        """

        if resource is None:
            resource = self.env['resource.resource']

        assert dt.tzinfo, 'Provided datetimes needs to be timezoned'
        dt = dt.astimezone(timezone(self.tz))

        range_start = dt + relativedelta(hour=0, minute=0, second=0)
        range_end = dt + relativedelta(days=1, hour=0, minute=0, second=0)

        for interval in self._work_intervals_batch(range_start, range_end, resource)[resource.id]:
            if interval[0] <= dt <= interval[1]:
                return True
        return False

