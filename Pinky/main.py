import utime

import config
from pinky_display import PinkyDisplay
from wifi_helper import connect_wifi, disconnect_wifi


def _load_framebuffer_bytes(debug_log: list) -> bytes:
    source = str(getattr(config, "FRAMEBUFFER_SOURCE", "local")).strip().lower()
    debug_log.append("Source: {}".format(source))

    if source == "local":
        filename = str(getattr(config, "LOCAL_FRAMEBUFFER_FILENAME", "")).strip()
        if not filename:
            raise ValueError("LOCAL_FRAMEBUFFER_FILENAME is not set")
        debug_log.append("File: {}".format(filename))
        with open(filename, "rb") as f:
            data = f.read()
        debug_log.append("Loaded {} bytes".format(len(data)))
        return data

    if source == "wifi":
        import secrets
        import urequests
        
        ssid = getattr(secrets, "WIFI_SSID", "")
        if not ssid:
            raise ValueError("WiFi SSID not set")
        debug_log.append("SSID: {}".format(ssid))
        
        password = getattr(secrets, "WIFI_PASSWORD", "")
        if not password:
            raise ValueError("WiFi password not set")
        debug_log.append("Password: [set]")
        
        debug_log.append("Connecting...")
        if not connect_wifi(ssid, password):
            raise RuntimeError("Failed to connect to WiFi")
        debug_log.append("Connected")
        
        try:
            url = getattr(config, "FLETCHER_LATEST_BIN_URL", "")
            if not url:
                raise ValueError("FLETCHER_LATEST_BIN_URL not set")
            debug_log.append("URL: {}".format(url))
            
            debug_log.append("Fetching...")
            resp = urequests.get(url)
            try:
                status = getattr(resp, "status_code", 200)
                debug_log.append("HTTP {}".format(status))
                if status != 200:
                    raise ValueError("HTTP status {}".format(status))
                data = resp.content
                debug_log.append("Got {} bytes".format(len(data)))
                return data
            finally:
                try:
                    resp.close()
                except Exception:
                    pass
        finally:
            debug_log.append("Disconnecting...")
            disconnect_wifi()
            debug_log.append("Disconnected")

    raise ValueError("Unknown FRAMEBUFFER_SOURCE")


def main():
    display = PinkyDisplay()
    display.clear()
    
    debug_log = []
    error_msg = None
    framebuffer_data = None
    
    debug_log.append("Pinky starting...")
    debug_log.append("")
    
    try:
        framebuffer_data = _load_framebuffer_bytes(debug_log)
        debug_log.append("")
        debug_log.append("Success! Should update in approximately 60 seconds")
    except Exception as e:
        error_msg = str(e)
        debug_log.append("")
        debug_log.append("ERROR:")
        debug_log.append(error_msg)
    
    y = 5
    for line in debug_log:
        display.text_black(line, 5, y)
        y += 10
    
    display.show()
    utime.sleep_ms(60000)
    
    if error_msg is None and framebuffer_data is not None:
        display.clear()
        display.set_black_framebuffer_bytes(framebuffer_data)
        display.show()
        utime.sleep_ms(20000)
    
    display.sleep()


main()
