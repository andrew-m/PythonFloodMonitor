import utime

import config
from pinky_display import PinkyDisplay
from wifi_helper import connect_wifi, disconnect_wifi


def _check_if_updated(url: str, last_modified: str) -> tuple:
    """Check if URL has been modified since last_modified timestamp using HTTP HEAD.
    
    Returns (has_changed: bool, new_timestamp: str)
    """
    import urequests
    
    try:
        resp = urequests.head(url)
        try:
            status = getattr(resp, "status_code", 0)
            if status != 200:
                return (True, "")
            
            headers = getattr(resp, "headers", {})
            current_modified = headers.get("Last-Modified", headers.get("last-modified", ""))
            
            if not current_modified or not last_modified:
                return (True, current_modified)
            
            return (current_modified != last_modified, current_modified)
        finally:
            try:
                resp.close()
            except Exception:
                pass
    except Exception:
        return (True, "")


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
                
                headers = getattr(resp, "headers", {})
                last_modified = headers.get("Last-Modified", headers.get("last-modified", ""))
                
                return (data, last_modified)
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


def _run_once(display: PinkyDisplay, last_modified: str, show_debug: bool = True) -> tuple:
    """Run one fetch/display cycle.
    
    Returns (success: bool, new_last_modified: str)
    """
    debug_log = []
    error_msg = None
    framebuffer_data = None
    new_last_modified = last_modified
    
    source = str(getattr(config, "FRAMEBUFFER_SOURCE", "local")).strip().lower()
    
    if source == "wifi":
        import secrets
        
        url = getattr(config, "FLETCHER_LATEST_BIN_URL", "")
        
        if last_modified and url:
            debug_log.append("Checking for updates...")
            
            ssid = getattr(secrets, "WIFI_SSID", "")
            password = getattr(secrets, "WIFI_PASSWORD", "")
            
            if ssid and password:
                try:
                    if connect_wifi(ssid, password):
                        debug_log.append("Connected")
                        try:
                            has_changed, new_timestamp = _check_if_updated(url, last_modified)
                            if not has_changed:
                                disconnect_wifi()
                                return (True, last_modified)
                            debug_log.append("Update available")
                            if new_timestamp:
                                new_last_modified = new_timestamp
                        finally:
                            disconnect_wifi()
                except Exception:
                    pass
    
    debug_log.append("Fetching data...")
    debug_log.append("")
    
    try:
        result = _load_framebuffer_bytes(debug_log)
        if source == "wifi" and isinstance(result, tuple):
            framebuffer_data, timestamp = result
            if timestamp:
                new_last_modified = timestamp
        else:
            framebuffer_data = result
        debug_log.append("")
        debug_log.append("Success! Update in approx 60s")
    except Exception as e:
        error_msg = str(e)
        debug_log.append("")
        debug_log.append("ERROR:")
        debug_log.append(error_msg)
    
    if error_msg is not None:
        display.clear()
        y = 5
        for line in debug_log:
            display.text_black(line, 5, y)
            y += 10
        display.show()
        return (False, last_modified)
    
    if framebuffer_data is not None:
        if show_debug:
            display.clear()
            y = 5
            for line in debug_log:
                display.text_black(line, 5, y)
                y += 10
            display.show()
            utime.sleep_ms(60000)
        
        display.clear()
        display.set_black_framebuffer_bytes(framebuffer_data)
        display.show()
        return (True, new_last_modified)
    
    return (False, last_modified)


def main():
    display = PinkyDisplay()
    display.clear()
    
    scheduled_mode = getattr(config, "SCHEDULED_MODE", False)
    check_interval_s = getattr(config, "SCHEDULE_CHECK_INTERVAL_S", 5 * 60)
    
    last_modified = ""
    
    if not scheduled_mode:
        _run_once(display, last_modified, show_debug=True)
        utime.sleep_ms(20000)
        display.sleep()
        return
    
    first_run = True
    while True:
        success, last_modified = _run_once(display, last_modified, show_debug=first_run)
        first_run = False
        
        if not success:
            display.sleep()
            break
        
        utime.sleep(check_interval_s)


main()
