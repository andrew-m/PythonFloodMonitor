import io
import os
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    raise ImportError(
        "Pillow (PIL) is required to render PNGs. Ensure the Lambda has the Pillow layer attached."
    ) from e


def _format_utc(ts: str) -> str:
    try:
        dt = datetime.fromisoformat(str(ts).replace("Z", "+00:00"))
        return dt.strftime("%H:%M %d %b")
    except Exception:
        return str(ts)


def _load_large_font(size: int = 40):
    try:
        here = os.path.dirname(__file__)
        font_path = os.path.join(here, "fonts", "Jersey20-Regular.ttf")
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def _load_label_font(size: int = 16):
    try:
        here = os.path.dirname(__file__)
        font_path = os.path.join(here, "fonts", "Silkscreen-Regular.ttf")
        return ImageFont.truetype(font_path, size)
    except Exception:
        return ImageFont.load_default()


def _draw_large_height(draw: "ImageDraw.ImageDraw", font: "ImageFont.ImageFont", value_m: float, decimal_x: int, y: int):
    s = f"{float(value_m):.2f}"
    if "." in s:
        int_part, frac_part = s.split(".", 1)
    else:
        int_part, frac_part = s, "00"

    dot = "."
    try:
        int_w = draw.textlength(int_part, font=font)
        dot_w = draw.textlength(dot, font=font)
    except Exception:
        int_w = font.getlength(int_part)
        dot_w = font.getlength(dot)

    draw.text((decimal_x - int_w, y), int_part, fill="black", font=font)
    draw.text((decimal_x, y), dot, fill="black", font=font)
    draw.text((decimal_x + dot_w, y), frac_part, fill="black", font=font)


def _draw_station_graph(draw: "ImageDraw.ImageDraw", font: "ImageFont.ImageFont", station: dict, x0: int, y0: int):
    heights = station.get("heights_m") or []
    y_axis_top_m = station.get("y_axis_top_m")
    y_axis_bottom_m = station.get("y_axis_bottom_m")
    top_of_normal_range_m = station.get("top_of_normal_range_m")
    highest_ever_recorded_m = station.get("highest_ever_recorded_m")
    first_ts = station.get("first_timestamp_utc", "")
    last_ts = station.get("last_timestamp_utc", "")

    title_h = 12
    label_h = 12
    graph_width = 200
    graph_height = 100

    title_y = y0
    top_y = y0 + title_h
    base_y = top_y + graph_height
    x_axis_end = x0 + graph_width

    old_fontmode = getattr(draw, "fontmode", None)
    try:
        draw.fontmode = "1"
    except Exception:
        pass

    draw.text((x0, title_y), str(station.get("name", "")), fill="black", font=font)

    draw.line([(x0, base_y), (x_axis_end, base_y)], fill="black", width=1)
    draw.line([(x0, base_y), (x0, top_y)], fill="black", width=1)
    draw.line([(x_axis_end, base_y), (x_axis_end, top_y)], fill="black", width=1)

    first_label = _format_utc(first_ts)
    last_label = _format_utc(last_ts)
    draw.text((x0, base_y + 2), first_label, fill="black", font=font)
    draw.text((x_axis_end - 80, base_y + 2), last_label, fill="black", font=font)

    if not isinstance(y_axis_bottom_m, (int, float)):
        y_axis_bottom_m = 0.0

    if (
        isinstance(y_axis_top_m, (int, float))
        and isinstance(y_axis_bottom_m, (int, float))
        and y_axis_top_m > y_axis_bottom_m
    ):
        y_range = float(y_axis_top_m) - float(y_axis_bottom_m)
        draw.text((x_axis_end + 5, base_y - 6), f"{float(y_axis_bottom_m):g}m", fill="black", font=font)
        draw.text((x_axis_end + 5, top_y - 6), f"{y_axis_top_m:g}m", fill="black", font=font)

        def draw_ref_line(value_m, label: str):
            if not isinstance(value_m, (int, float)):
                return
            if value_m < 0:
                return

            y = base_y - int(round(((float(value_m) - float(y_axis_bottom_m)) / y_range) * graph_height))
            if y < top_y:
                y = top_y
            if y > base_y:
                y = base_y

            draw.line([(x0, y), (x_axis_end + 15, y)], fill="black", width=1)
            label_x = x_axis_end + 20
            draw.text((label_x, y - 6), f"{float(value_m):g}m", fill="black", font=font)
            draw.text((label_x, y + 6), label, fill="black", font=font)

        draw_ref_line(top_of_normal_range_m, "Normal")
        draw_ref_line(highest_ever_recorded_m, "Record")

    try:
        if old_fontmode is not None:
            draw.fontmode = old_fontmode
    except Exception:
        pass

    if (
        isinstance(y_axis_top_m, (int, float))
        and isinstance(y_axis_bottom_m, (int, float))
        and y_axis_top_m > y_axis_bottom_m
        and len(heights) == 200
    ):
        y_range = float(y_axis_top_m) - float(y_axis_bottom_m)
        for i, h in enumerate(heights):
            x = x0 + 1 + i
            try:
                v = float(h)
            except Exception:
                continue

            bar_h = int(round(((v - float(y_axis_bottom_m)) / y_range) * graph_height))
            if bar_h < 0:
                bar_h = 0
            if bar_h > graph_height:
                bar_h = graph_height
            if bar_h == 0:
                continue

            draw.line([(x, base_y), (x, base_y - bar_h)], fill="black", width=1)

    return title_h + graph_height + label_h


def _render_latest_image(river_doc: dict) -> "Image.Image":
    img = Image.new("RGB", (400, 300), "white")
    draw = ImageDraw.Draw(img)
    label_font = _load_label_font(8)
    large_font = _load_large_font(70)
    station_font = _load_large_font(26)
    small_font = _load_label_font(8)

    utc_time = river_doc.get("utc_time", "")
    try:
        dt = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
        time_label = dt.strftime("%I:%M %p").lstrip("0")
        date_label = dt.strftime("%d %b %Y")
    except Exception:
        time_label = str(utc_time)
        date_label = ""

    try:
        time_w = draw.textlength(time_label, font=station_font)
    except Exception:
        time_w = station_font.getlength(time_label)

    updated_date_label = f"Updated {date_label}".strip()
    try:
        updated_date_w = draw.textlength(updated_date_label, font=small_font)
    except Exception:
        updated_date_w = small_font.getlength(updated_date_label)

    right_margin = 10
    x_time = 400 - right_margin - time_w
    x_updated_date = 400 - right_margin - updated_date_w

    old_fontmode = getattr(draw, "fontmode", None)
    try:
        draw.fontmode = "1"
    except Exception:
        pass

    draw.text((x_updated_date, 1), updated_date_label, fill="black", font=small_font)
    draw.text((x_time, 15), time_label, fill="black", font=station_font)

    try:
        if old_fontmode is not None:
            draw.fontmode = old_fontmode
    except Exception:
        pass

    stations = river_doc.get("stations") or []
    x0 = 10
    y0 = 20
    gap = 15
    decimal_x = 310

    if len(stations) >= 1:
        used_h = _draw_station_graph(draw, label_font, stations[0], x0=x0, y0=y0)
        heights_0 = stations[0].get("heights_m") or []
        if heights_0:
            station_name_0 = str(stations[0].get("name", "")).strip()
            short_0 = (station_name_0.split() or [""])[0]

            old_fontmode = getattr(draw, "fontmode", None)
            try:
                draw.fontmode = "1"
            except Exception:
                pass

            draw.text((decimal_x - 25, y0 + 28), short_0, fill="black", font=station_font)
            _draw_large_height(draw, large_font, float(heights_0[-1]), decimal_x=decimal_x, y=y0 + 48)

            try:
                if old_fontmode is not None:
                    draw.fontmode = old_fontmode
            except Exception:
                pass
        y0 = y0 + used_h + gap

    if len(stations) >= 2:
        _draw_station_graph(draw, label_font, stations[1], x0=x0, y0=y0)
        heights_1 = stations[1].get("heights_m") or []
        if heights_1:
            station_name_1 = str(stations[1].get("name", "")).strip()
            short_1 = (station_name_1.split() or [""])[0]

            old_fontmode = getattr(draw, "fontmode", None)
            try:
                draw.fontmode = "1"
            except Exception:
                pass

            draw.text((decimal_x - 25, y0 + 28), short_1, fill="black", font=station_font)
            _draw_large_height(draw, large_font, float(heights_1[-1]), decimal_x=decimal_x, y=y0 + 48)

            try:
                if old_fontmode is not None:
                    draw.fontmode = old_fontmode
            except Exception:
                pass

    return img


def render_latest_png(river_doc: dict) -> bytes:
    img = _render_latest_image(river_doc)
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


def render_latest_mono_hlsb_black(river_doc: dict) -> bytes:
    img = _render_latest_image(river_doc)
    mono = img.convert("1", dither=Image.Dither.NONE)
    width, height = mono.size
    if width != 400 or height != 300:
        raise ValueError(f"Expected 400x300 image, got {width}x{height}")

    pixels = mono.load()
    out = bytearray((width * height) // 8)

    idx = 0
    for y in range(height):
        for x_byte in range(0, width, 8):
            b = 0
            for bit in range(8):
                x = x_byte + bit
                px = pixels[x, y]
                if px:
                    b |= 1 << (7 - bit)
            out[idx] = b
            idx += 1

    return bytes(out)
