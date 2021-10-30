from network import WLAN, STA_IF, AP_IF
from dawndoor import data


def is_connected():
    """
    Check if the WLAN is connected to a network
    """
    wlan = WLAN(STA_IF)
    return wlan.active() and wlan.isconnected()


def connect():
    """
    Connect to the WiFi network based on the configuration. Fails silently if there is no configuration.
    """
    network_config = data.get_network()
    if not network_config:
        return
    try:
        wlan = WLAN(STA_IF)
        if wlan.active() and wlan.isconnected():
            return
        wlan.active(True)
        wlan.connect(network_config['essid'], network_config['password'])
    except Exception:
        pass


def get_ip():
    """
    Get the IP address for the current active WLAN
    """
    ip_address = None
    wlan = WLAN(STA_IF)
    if wlan.active() and wlan.isconnected():
        details = wlan.ifconfig()
        ip_address = details[0] if details else None
    return ip_address


def get_ap_ip():
    """
    Get the IP address of the Access Point, if it is running
    """
    ip_address = None
    ap = WLAN(AP_IF)
    if ap.active():
        details = ap.ifconfig()
        ip_address = details[0] if details else None
    return ip_address


def start_ap():
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    ap = WLAN(AP_IF)
    ap.active(True)
    ap.config(essid='DawnDoor', password='dawndoor')


def stop_ap():
    """
    Set up a WiFi Access Point so that you can initially connect to the device and configure it.
    """
    ap = WLAN(AP_IF)
    ap.active(False)
