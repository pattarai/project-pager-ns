import json


def _load_db():
    """
    Context manager to return an instance of a database
    """
    try:
        with open('/data/dawndoor.json', 'r') as f:
            db = json.load(f)
    except OSError:
        db = {}
    return db


def _save_db(db):
    with open('/data/dawndoor.json', 'w') as f:
        json.dump(db, f)


def has_config():
    """
    Determine if there is existing configuration
    """
    return bool(_load_db())


def get_location():
    """
    Load the location info from flash
    """
    return _load_db().get('location')


def save_location(latitude=None, longitude=None, timezone=None):
    """
    Save the timezone to the filesystem
    """
    db = _load_db()
    db['location'] = {
        'latitude': latitude,
        'longitude': longitude,
        'timezone': timezone
    }
    _save_db(db)


def get_network():
    """
    Get the WiFi config. If there is none, return None.
    """
    return _load_db().get('network')


def save_network(**kwargs):
    """
    Write the network config to file
    """
    db = _load_db()
    config = db.get('network')
    if not config:
        config = {}
    config.update(kwargs)
    db['network'] = config
    _save_db(db)


def get_door_status():
    """
    Load the current status of the door
    """
    door_status = _load_db().get('door_status')
    if not door_status:
        door_status = 'Closed'
    return door_status


def save_door_status(door_status):
    """
    Save the current door status
    """
    db = _load_db()
    db['door_status'] = door_status
    _save_db(db)


def get_door_config():
    """
    Load the door configuration
    """
    return _load_db().get('door_config', {})


def save_door_config(door_config):
    """
    Save the door configuration
    """
    db = _load_db()
    db['door_config'] = door_config
    _save_db(db)


def get_sunrise_sunset(date):
    """
    Get the sunrise and sunset for the day
    """
    data = _load_db().get('sunrise_sunset')
    if data and str(date) in data:
        return data[str(date)]
    else:
        return None


def save_sunrise_sunset(sunrise, sunset):
    """
    Save the sunrise and sunset for the day
    """
    date = str(sunrise)
    db = _load_db()
    db['sunrise_sunset'] = {
        date: {
            'sunrise': sunrise.serialize(),
            'sunset': sunset.serialize()
        }
    }
    _save_db(db)
