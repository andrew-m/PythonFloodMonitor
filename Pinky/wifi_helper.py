import network
import utime


def connect_wifi(ssid: str, password: str, timeout_s: int = 30) -> bool:
    """Connect to WiFi network. Returns True if successful, False otherwise."""
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    
    if wlan.isconnected():
        return True
    
    wlan.connect(ssid, password)
    
    start = utime.time()
    while not wlan.isconnected():
        if utime.time() - start > timeout_s:
            return False
        utime.sleep_ms(500)
    
    return True


def disconnect_wifi():
    """Disconnect from WiFi and deactivate interface to save power."""
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        wlan.disconnect()
    wlan.active(False)
