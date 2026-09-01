import utime

import config
from pinky_display import PinkyDisplay
from wifi_helper import connect_wifi, disconnect_wifi


def _debug_tail(lines: list, max_lines: int) -> list:
    if max_lines <= 0:
        return []
    if len(lines) <= max_lines:
        return lines
    return lines[-max_lines:]


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
        import gc
        
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
            gc.collect()
        except Exception:
            pass
        try:
            debug_log.append("mem_free: {}".format(gc.mem_free()))
        except Exception:
            pass
        
        try:
            use_3color = getattr(config, "USE_3COLOR", False)
            if use_3color:
                url = getattr(config, "FLETCHER_LATEST_3C_BIN_URL", "")
                if not url:
                    raise ValueError("FLETCHER_LATEST_3C_BIN_URL not set")
                debug_log.append("Mode: 3-color")
            else:
                url = getattr(config, "FLETCHER_LATEST_BIN_URL", "")
                if not url:
                    raise ValueError("FLETCHER_LATEST_BIN_URL not set")
                debug_log.append("Mode: 2-color")
            debug_log.append("URL: {}".format(url))
            
            debug_log.append("Fetching...")
            try:
                resp = urequests.get(url)
            except Exception as e:
                debug_log.append("GET exception: {}: {}".format(type(e).__name__, repr(e)))
                raise
            try:
                status = getattr(resp, "status_code", 200)
                debug_log.append("HTTP {}".format(status))
                if status != 200:
                    raise ValueError("HTTP status {}".format(status))
                try:
                    data = resp.content
                except Exception as e:
                    debug_log.append("Read content exception: {}: {}".format(type(e).__name__, repr(e)))
                    try:
                        debug_log.append("mem_free: {}".format(gc.mem_free()))
                    except Exception:
                        pass
                    raise
                debug_log.append("Got {} bytes".format(len(data)))
                try:
                    debug_log.append("mem_free: {}".format(gc.mem_free()))
                except Exception:
                    pass
                
                headers = getattr(resp, "headers", {})
                last_modified = headers.get("Last-Modified", headers.get("last-modified", ""))
                
                return (data, last_modified)
            finally:
                try:
                    resp.close()
                except Exception as e:
                    debug_log.append("resp.close exception: {}: {}".format(type(e).__name__, repr(e)))
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
        import urequests
        
        use_3color = getattr(config, "USE_3COLOR", False)
        if use_3color:
            url = getattr(config, "FLETCHER_LATEST_3C_BIN_URL", "")
        else:
            url = getattr(config, "FLETCHER_LATEST_BIN_URL", "")
        
        if last_modified and url:
            debug_log.append("Checking for updates...")
            
            ssid = getattr(secrets, "WIFI_SSID", "")
            password = getattr(secrets, "WIFI_PASSWORD", "")
            
            if ssid and password:
                try:
                    connected = False
                    try:
                        connected = bool(connect_wifi(ssid, password))
                    except Exception as e:
                        debug_log.append("WiFi connect exception: {}: {}".format(type(e).__name__, str(e)))
	
                    if connected:
                        try:
                            try:
                                has_changed, new_timestamp = _check_if_updated(url, last_modified)
                                debug_log.append("HEAD: changed={}".format(has_changed))
                                if new_timestamp:
                                    debug_log.append("HEAD: Last-Modified present")
                            except Exception as e:
                                debug_log.append("HEAD exception: {}: {}".format(type(e).__name__, str(e)))
                                raise
	
                            if not has_changed:
                                debug_log.append("No update")
                                return (True, last_modified)

                            debug_log.append("Update available")
                            if new_timestamp:
                                new_last_modified = new_timestamp

                            debug_log.append("Fetching data...")
                            debug_log.append("")

                            debug_log.append("Fetching...")
                            try:
                                resp = urequests.get(url)
                            except Exception as e:
                                debug_log.append("GET exception: {}: {}".format(type(e).__name__, repr(e)))
                                raise
                            try:
                                status = getattr(resp, "status_code", 200)
                                debug_log.append("HTTP {}".format(status))
                                if status != 200:
                                    raise ValueError("HTTP status {}".format(status))
                                framebuffer_data = resp.content
                                debug_log.append("Got {} bytes".format(len(framebuffer_data)))

                                headers = getattr(resp, "headers", {})
                                ts = headers.get("Last-Modified", headers.get("last-modified", ""))
                                if ts:
                                    new_last_modified = ts
                            finally:
                                try:
                                    resp.close()
                                except Exception as e:
                                    debug_log.append("resp.close exception: {}: {}".format(type(e).__name__, repr(e)))
                        finally:
                            try:
                                disconnect_wifi()
                            except Exception as e:
                                debug_log.append("WiFi disconnect exception: {}: {}".format(type(e).__name__, str(e)))
                    else:
                        debug_log.append("WiFi: connect failed")
                except Exception as e:
                    debug_log.append("Update-check exception: {}: {}".format(type(e).__name__, str(e)))
	    
    if framebuffer_data is None:
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
            debug_log.append("Success! Update in approx 20s")
        except Exception as e:
            error_msg = str(e)
            if not error_msg:
                error_msg = "{}: {}".format(type(e).__name__, repr(e))
            else:
                error_msg = "{}: {}".format(type(e).__name__, error_msg)
            debug_log.append("")
            debug_log.append("ERROR:")
            debug_log.append(error_msg)
    else:
        debug_log.append("")
        debug_log.append("Success! Update in approx 20s")
    
    if error_msg is not None:
        display.clear()
        y = 5
        for line in _debug_tail(debug_log, 24):
            display.text_black(line, 5, y)
            y += 10
        display.show()
        return (False, last_modified)
    
    if framebuffer_data is not None:
        if show_debug:
            display.clear()
            y = 5
            for line in _debug_tail(debug_log, 24):
                display.text_black(line, 5, y)
                y += 10
            display.show()
            utime.sleep_ms(20000)
        
        display.clear()
        use_3color = getattr(config, "USE_3COLOR", False)
        if use_3color:
            display.set_3color_framebuffer_bytes(framebuffer_data)
        else:
            display.set_black_framebuffer_bytes(framebuffer_data)
        display.show()
        return (True, new_last_modified)
    
    return (False, last_modified)


def main():
    display = PinkyDisplay()
    display.clear()
    
    scheduled_mode = getattr(config, "SCHEDULED_MODE", False)
    check_interval_s = getattr(config, "SCHEDULE_CHECK_INTERVAL_S", 5 * 60)
    error_retry_delay_s = getattr(config, "ERROR_RETRY_DELAY_S", 5 * 60)
    current_retry_delay_s = error_retry_delay_s
    
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
            try:
                display.sleep()
            except Exception:
                pass

            utime.sleep_ms(int(current_retry_delay_s * 1000))
            current_retry_delay_s = min(current_retry_delay_s * 2, error_retry_delay_s * 16)

            display = PinkyDisplay()
            display.clear()
            last_modified = ""
            first_run = True
            continue
        else:
            current_retry_delay_s = error_retry_delay_s
        
        utime.sleep_ms(check_interval_s * 1000)


main()
