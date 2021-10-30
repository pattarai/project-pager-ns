# -*- coding: utf-8 -*-
"""
This module is based on https://github.com/jebeaudet/SunriseSunsetCalculator, modified to work
with MicroPython (and it's lack of CPython objects)

This module calculates the times of sunrise and sunset given a location and date.
"""
import math
from dawndoor.datetime import DateTime

CIVIL_ZENITH = 90.83333


def calculate_sunrise_sunset(date, latitude, longitude, timezone=0):
    """
    Computes the sunset and sunrise for the current day, in local time
    """
    if not date:
        date = DateTime.now()
    if latitude < -90:
        latitude = -90
    if latitude > 90:
        latitude = 90
    if longitude < -180:
        longitude = -180
    if longitude > 180:
        longitude = 180
    if timezone < -12:
        timezone = -12
    if timezone > 14:
        timezone = 14

    # Calculate the day of the year
    day_of_year = date.doy

    # Convert the longitude to hour value and calculate an approximate time
    longitude_hour = longitude / 15
    approx_rise = day_of_year + ((6 - longitude_hour) / 24)
    approx_set = day_of_year + ((18 - longitude_hour) / 24)

    # Calculate the Sun's mean anomaly
    mean_rise = (0.9856 * approx_rise) - 3.289
    mean_set = (0.9856 * approx_set) - 3.289

    # Calculate the Sun's true longitude, and adjust angle to be between 0
    # and 360
    long_rise = (mean_rise + (1.916 * math.sin(math.radians(mean_rise))) +
                 (0.020 * math.sin(math.radians(2 * mean_rise))) + 282.634) % 360
    long_set = (mean_set + (1.916 * math.sin(math.radians(mean_set))) +
                (0.020 * math.sin(math.radians(2 * mean_set))) + 282.634) % 360

    # Calculate the Sun's right ascension, and adjust angle to be between 0 and
    # 360
    right_ascension_rise = (math.degrees(math.atan(0.91764 * math.tan(math.radians(long_rise))))) % 360
    right_ascension_set = (math.degrees(math.atan(0.91764 * math.tan(math.radians(long_set))))) % 360

    # Right ascension value needs to be in the same quadrant as L
    long_quadrant_rise = (math.floor(long_rise/90)) * 90
    right_ascension_quadrant_rise = (math.floor(right_ascension_rise/90)) * 90
    right_ascension_rise = right_ascension_rise + (long_quadrant_rise - right_ascension_quadrant_rise)

    long_quadrant_set = (math.floor(long_set/90)) * 90
    right_ascension_quadrant_set = (math.floor(right_ascension_set/90)) * 90
    right_ascension_set = right_ascension_set + (long_quadrant_set - right_ascension_quadrant_set)

    # Right ascension value needs to be converted into hours
    right_ascension_rise = right_ascension_rise / 15
    right_ascension_set = right_ascension_set / 15

    # Calculate the Sun's declination
    sin_declination_rise = 0.39782 * math.sin(math.radians(long_rise))
    cos_declination_rise = math.cos(math.asin(sin_declination_rise))

    sin_declination_set = 0.39782 * math.sin(math.radians(long_set))
    cos_declination_set = math.cos(math.asin(sin_declination_set))

    # Calculate the Sun's local hour angle
    cos_zenith = math.cos(math.radians(CIVIL_ZENITH))
    radian_lat = math.radians(latitude)
    sin_latitude = math.sin(radian_lat)
    cos_latitude = math.cos(radian_lat)
    cos_hour_angle_rise = (cos_zenith - (sin_declination_rise * sin_latitude)) / (cos_declination_rise * cos_latitude)
    cos_hour_angle_set = (cos_zenith - (sin_declination_set * sin_latitude)) / (cos_declination_set * cos_latitude)

    # Finish calculating H and convert into hours
    hour_angle_rise = (360 - math.degrees(math.acos(cos_hour_angle_rise))) / 15
    hour_angle_set = math.degrees(math.acos(cos_hour_angle_set)) / 15

    # Calculate local mean time of rising/setting
    mean_time_rise = hour_angle_rise + right_ascension_rise - (0.06571 * approx_rise) - 6.622
    mean_time_set = hour_angle_set + right_ascension_set - (0.06571 * approx_set) - 6.622

    # Adjust back to UTC, and keep the time between 0 and 24
    utc_rise = (mean_time_rise - longitude_hour) % 24
    utc_set = (mean_time_set - longitude_hour) % 24

    # Convert UT value to local time zone of latitude/longitude
    local_time_rise = (utc_rise + timezone) % 24
    local_time_set = (utc_set + timezone) % 24

    # Conversion
    hour_rise = int(local_time_rise)
    minute_rise = int(local_time_rise % 1 * 60)
    hour_set = int(local_time_set)
    minute_set = int(local_time_set % 1 * 60)

    # Create datetime objects with same date, but with hour and minute
    # specified
    rise_dt = date.replace(hour=hour_rise, minute=minute_rise)
    set_dt = date.replace(hour=hour_set, minute=minute_set)
    return rise_dt, set_dt


__all__ = ['calculate_sunrise_sunset']
