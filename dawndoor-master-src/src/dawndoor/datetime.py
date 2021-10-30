"""
This module contains date and time related functions
"""
import time

TIMEZONES = {
    'PST': {
        'name': 'Pacific time',
        'offset': -8,
        'dst': True
    },
    'MST': {
        'name': 'Mountain time',
        'offset': -7,
        'dst': True
    },
    'AMT': {
        'name': 'Arizona time',  # Arizona time has no DST
        'offset': -7,
        'dst': False
    },
    'CST': {
        'name': 'Central time',
        'offset': -6,
        'dst': True
    },
    'EST': {
        'name': 'Eastern time',
        'offset': -5,
        'dst': True
    },
    'AST': {
        'name': 'Atlantic time',
        'offset': -4,
        'dst': True
    }
}


class Timezone(object):
    """
    A basic timezone object
    """
    def __init__(self, name, offset, has_dst=True):
        self.name = name
        self.offset = offset
        self.has_dst = has_dst


class Time(object):
    """
    A basic time object
    """
    def __init__(self, hour=None, minute=None, second=None):
        self.hour = hour
        self.minute = minute
        self.second = second


class Date(object):
    """
    A basic date object
    """
    def __init__(self, year=None, month=None, day=None, dow=None, doy=None):
        """
        Initialise the object
        """
        self.year = year
        self.month = month
        self.day = day
        if not dow and (year and month and day):
            # Get seconds since epoch, and run that back to localtime to get day of week
            self.dow = time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0)))[6]
        else:
            self.dow = dow
        if not doy and (year and month and day):
            # Get seconds since epoch, and run that back to localtime to get day of year
            self.doy = time.localtime(time.mktime((year, month, day, 0, 0, 0, 0, 0)))[7]
        else:
            self.doy = doy

    @classmethod
    def today(cls):
        """
        Return a pre-populated date object for today
        """
        timestamp = time.localtime()
        return Date(timestamp[0], timestamp[1], timestamp[3], timestamp[6], timestamp[7])

    def __str__(self):
        """
        Return a string representing the day
        """
        return '{y}-{m:0>2}-{d:0>2}'.format(y=self.year, m=self.month, d=self.day)


class DateTime(Date):
    """
    A basic object to hold a date and time
    """
    def __init__(self, year=None, month=None, day=None, hour=None, minute=None, second=None, dow=None, doy=None):
        """
        Initialise the object
        """
        super().__init__(year, month, day, dow, doy)
        self.hour = hour
        self.minute = minute
        self.second = second

    @classmethod
    def now(cls):
        """
        Instantiate a new DateTime class based on the current time
        """
        return DateTime(*time.localtime())

    def date(self):
        """
        Return a Date object of just the date
        """
        return Date(self.year, self.month, self.day)

    def time(self):
        """
        Return a Time object of just the time
        """
        return Time(self.hour, self.minute, self.second)

    def unixtime(self):
        """
        Return a unix timestamp
        """
        return time.mktime(
            (self.year or 0, self.month or 0, self.day or 0, self.hour or 0, self.minute or 0, self.second or 0,
             self.dow or 0, self.doy or 0)
        )

    def as_timezone(self, tz):
        """
        Return the time as per the timezone
        """
        offset = tz_to_offset(tz)
        if TIMEZONES.get(tz, {}).get('dst') and is_dst(self):
            offset += 1
        offset_secs = offset * 3600
        return DateTime(*time.gmtime(self.unixtime() + offset_secs))

    def replace(self, year=None, month=None, day=None, hour=None, minute=None, second=None, dow=None, doy=None):
        """
        Copy the built-in datetime object's replace method, adjusted for this object
        """
        return DateTime(year or self.year, month or self.month, day or self.day, hour or self.hour,
                        minute or self.minute, second or self.second, dow or self.dow, doy or self.doy)

    def serialize(self):
        """
        Convert datetime object into a dict, so that it can be fed back into the object later
        """
        obj = {}
        for attr in ['year', 'month', 'day', 'hour', 'minute', 'second', 'dow', 'doy']:
            val = getattr(self, attr)
            if val:
                obj[attr] = val
        return obj

    def __gt__(self, other):
        """
        Greater than operator
        """
        return self.unixtime() > other.unixtime()

    def __lt__(self, other):
        """
        Less than operator
        """
        return self.unixtime() < other.unixtime()


def is_dst(date):
    """
    Determine you are currently experiencing DST
    """
    if date.month < 3 or date.month > 11:
        # December to January are out
        return False
    if 3 < date.month < 11:
        return True
    if date.month == 3:
        return date.day - date.dow >= 8
    if date.month == 11:
        return date.day - date.dow <= 0
    return False


def tz_to_offset(timezone):
    """
    Convert a timezone to its offset
    """
    return TIMEZONES.get(timezone, {'offset': 0})['offset']


__all__ = ['Date', 'Time', 'DateTime', 'is_dst']
