# -*- coding: utf-8 -*-
# DawnDoor
# --------
# Copyright (C) 2021 Raoul Snyman
#
# Licensed under the MIT license, see LICENSE.txt for details
import gc
from machine import SoftI2C, Pin
from ssd1306 import SSD1306_I2C

try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from dawndoor import data
from dawndoor.astro import calculate_sunrise_sunset
from dawndoor.datetime import DateTime, tz_to_offset
from dawndoor.door import DoorStatus, open_door, close_door
from dawndoor.image import load_pbm
from dawndoor.state import State
from dawndoor.web import WebApp, jsonify
from dawndoor.wifi import connect, get_ip, get_ap_ip, start_ap, stop_ap, is_connected

webapp = WebApp()
state = State(
    is_ready=False,
    is_display_updated=False,
    is_time_set=False
)


@webapp.route('/', method='GET')
def index(request, response):
    """
    The main page
    """
    gc.collect()
    yield from webapp.sendfile(response, '/templates/index.html')


@webapp.route('/location', method='GET')
def get_location(request, response):
    """
    Get the location and timezone
    """
    location_data = data.get_location()
    gc.collect()
    yield from jsonify(response, location_data)


@webapp.route('/location', method='POST')
def save_location(request, response):
    """
    Save the location and timezone
    """
    yield from request.read_form_data()
    updated_data = {
        'latitude': int(request.form['latitude']),
        'longitude': int(request.form['longitude']),
        'timezone': request.form['timezone']
    }
    data.save_location(**updated_data)
    gc.collect()
    yield from jsonify(response, request.form)


@webapp.route('/network', method='GET')
def get_network(request, response):
    """
    Return the WiFi config
    """
    network_config = data.get_network()
    network_config['ip_address'] = get_ip()
    gc.collect()
    yield from jsonify(response, network_config)


@webapp.route('/network', method='POST')
def save_network(request, response):
    """
    Save the network config
    """
    yield from request.read_form_data()
    updated_config = {}
    for key in ['essid', 'password', 'can_start_ap']:
        if key in request.form:
            updated_config[key] = request.form[key]
    data.save_network(**updated_config)
    gc.collect()
    # Now try to connect to the WiFi network
    connect()
    gc.collect()
    if 'can_start_ap' in updated_config:
        updated_config['can_start_ap'] = updated_config['can_start_ap'].lower() == 'true'
        if updated_config['can_start_ap'] is False:
            stop_ap()
        else:
            start_ap()
    updated_config['ip_address'] = get_ip()
    gc.collect()
    yield from jsonify(response, updated_config)


@webapp.route('/door', method='GET')
def get_door_config(request, response):
    """
    Return the door status
    """
    door_data = data.get_door_config() or {'duration': 0}
    door_data['status'] = data.get_door_status() or '(unknown)'
    gc.collect()
    yield from jsonify(response, door_data)


@webapp.route('/door', method='POST')
def save_door_config(request, response):
    """
    Save the door config or status
    """
    yield from request.read_form_data()
    if request.form.get('action'):
        if request.form['action'] == 'open':
            open_door()
        elif request.form['action'] == 'close':
            close_door()
    elif 'status' in request.form:
        data.save_door_status(request.form['status'])
    gc.collect()
    updated_config = data.get_door_config()
    for key in ['duration']:
        if key in request.form:
            updated_config[key] = request.form[key]
    if updated_config:
        data.save_door_config(updated_config)
    updated_config['status'] = data.get_door_status()
    gc.collect()
    yield from jsonify(response, updated_config)


async def set_time():
    """
    Set the time from NTP
    """
    while True:
        if is_connected():
            from ntptime import settime
            settime()
            state.set('is_time_set', True)
            state.set('is_display_updated', True)
            print('Time set')
            gc.collect()
            await asyncio.sleep(3600)
        else:
            # If there's no connection, let's try again in a second
            print('No connection, retrying set_time in 1s')
            await asyncio.sleep(1)


async def calc_sunrise_sunset():
    """
    Periodically check if there's a sunrise/sunset file with the current date, and if not then generate it.
    """
    while True:
        if not state.get('is_time_set'):
            print('Time not set yet, retrying calc_sunrise_sunset in 5s')
            await asyncio.sleep(5)
            continue
        location = data.get_location()
        now = DateTime.now().as_timezone(location['timezone'])
        sun_data = data.get_sunrise_sunset(now)
        if location and not sun_data:
            print('Calculating sunrise and sunset')
            sunrise, sunset = calculate_sunrise_sunset(now, location['latitude'], location['longitude'],
                                                       tz_to_offset(location['timezone']))
            data.save_sunrise_sunset(sunrise, sunset)
            state.set('is_display_updated', True)
        gc.collect()
        await asyncio.sleep(3600)


async def door_check():
    """
    Check the time and either open or close the coop door
    """
    while True:
        if not state.get('is_time_set'):
            print('Time not set yet, retrying door_check in 5s')
            await asyncio.sleep(5)
            continue
        location = data.get_location()
        now = DateTime.now().as_timezone(location['timezone'])
        sun_data = data.get_sunrise_sunset(now)
        door_status = data.get_door_status()
        if sun_data:
            print('Checking door')
            sunrise = DateTime(**sun_data['sunrise'])
            sunset = DateTime(**sun_data['sunset'])
            if door_status == DoorStatus.Closed and now > sunrise and now < sunset:
                print('Opening door')
                await open_door()
            elif door_status == DoorStatus.Open and now > sunset:
                print('Closing door')
                await close_door()
            state.set('is_display_updated', True)
        gc.collect()
        await asyncio.sleep(300)


async def display_time():
    i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
    display = SSD1306_I2C(128, 64, i2c)
    # Show a splash screen first
    splash_logo = load_pbm('/images/dawndoor.pbm')
    display.fill(0)
    display.blit(splash_logo, 31, 0)
    display.show()
    while True:
        if not state.get('is_display_updated'):
            await asyncio.sleep(1)
            continue
        display.fill(0)
        if not data.has_config():
            ip = get_ap_ip()
            display.text('To set up:', 0, 0)
            display.text('WiFi: DawnDoor', 0, 10)
            display.text('Browser:', 0, 20)
            display.text(' ' + ip, 0, 30)
        else:
            ip = get_ip()
            door_status = data.get_door_status()
            location_data = data.get_location()
            now = DateTime.now().as_timezone(location_data['timezone'])
            sun_data = data.get_sunrise_sunset(now)
            display.text('DawnDoor', 0, 0)
            if is_connected():
                display.text('Connected', 0, 16)
                display.text(ip, 0, 26)
            else:
                display.text('Not connected', 0, 16)
            if sun_data:
                sunrise = DateTime(**sun_data['sunrise'])
                sunset = DateTime(**sun_data['sunset'])
                display.text('{:0>2}:{:0>2}'.format(sunrise.hour, sunrise.minute), 0, 46)
                display.text('{:0>2}:{:0>2}'.format(sunset.hour, sunset.minute), 88, 46)
            display.text(door_status, 0, 56)
            display.text('{:0>2}:{:0>2}'.format(now.hour, now.minute), 88, 56)
        display.show()
        gc.collect()
        await asyncio.sleep(1)


def main():
    """
    Set up the tasks and start the event loop
    """
    connect()
    loop = asyncio.get_event_loop()
    loop.create_task(display_time())
    loop.create_task(set_time())
    loop.create_task(calc_sunrise_sunset())
    loop.create_task(door_check())
    loop.create_task(asyncio.start_server(webapp.handle, '0.0.0.0', 80))
    gc.collect()
    loop.run_forever()
