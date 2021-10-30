import gc
try:
    import uasyncio as asyncio
except ImportError:
    import asyncio

from machine import Pin
from dawndoor.data import save_door_status, get_door_config

# D1 => GPIO5
RELAY_1 = Pin(5, mode=Pin.OUT, pull=None, value=False)
# D2 => GPIO4
RELAY_2 = Pin(4, mode=Pin.OUT, pull=None, value=False)


class DoorStatus(object):
    """
    Simple enumeration class for door status
    """
    Open = 'Open'
    Closed = 'Closed'

    @classmethod
    def invert(cls, status):
        """
        Invert the status
        """
        if status == cls.Open:
            return cls.Closed
        else:
            return cls.Open


async def _run_door(pin, final_status):
    """
    Open or close the door, and update the status

    :param pin: The pin to use
    :param final_status: The final status of the door (Open or Closed)
    """
    door_config = get_door_config()
    pin.on()
    await asyncio.sleep(door_config.get('duration', 10))
    pin.off()
    save_door_status(final_status)


async def open_door():
    """
    Open the door
    """
    await _run_door(RELAY_1, DoorStatus.Open)
    gc.collect()


async def close_door():
    """
    Close the door
    """
    await _run_door(RELAY_2, DoorStatus.Closed)
    gc.collect()
