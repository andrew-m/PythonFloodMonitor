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

    draw.text((x0, title_y), str(station.get("name", "")), fill="black", font=font)

    draw.line([(x0, base_y), (x_axis_end, base_y)], fill="black", width=1)
    draw.line([(x0, base_y), (x0, top_y)], fill="black", width=1)

    first_label = _format_utc(first_ts)
    last_label = _format_utc(last_ts)
    draw.text((x0, base_y + 2), first_label, fill="black", font=font)
    draw.text((x_axis_end - 80, base_y + 2), last_label, fill="black", font=font)

    draw.text((x_axis_end + 5, base_y - 6), "0m", fill="black", font=font)
    if isinstance(y_axis_top_m, (int, float)) and y_axis_top_m > 0:
        draw.text((x_axis_end + 5, top_y - 6), f"{y_axis_top_m:g}m", fill="black", font=font)

        def draw_ref_line(value_m, label: str):
            if not isinstance(value_m, (int, float)):
                return
            if value_m < 0:
                return

            y = base_y - int(round((float(value_m) / float(y_axis_top_m)) * graph_height))
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

    if isinstance(y_axis_top_m, (int, float)) and y_axis_top_m > 0 and len(heights) == 200:
        for i, h in enumerate(heights):
            x = x0 + 1 + i
            try:
                v = float(h)
            except Exception:
                continue

            bar_h = int(round((v / float(y_axis_top_m)) * graph_height))
            if bar_h < 0:
                bar_h = 0
            if bar_h > graph_height:
                bar_h = graph_height
            if bar_h == 0:
                continue

            draw.line([(x, base_y), (x, base_y - bar_h)], fill="black", width=1)

    return title_h + graph_height + label_h


def render_latest_png(river_doc: dict) -> bytes:
    img = Image.new("RGB", (400, 300), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    large_font = _load_large_font(70)
    station_font = _load_large_font(26)

    utc_time = river_doc.get("utc_time", "")
    try:
        dt = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
        human_time = dt.strftime("%H:%M %a %d %b %Y")
    except Exception:
        human_time = str(utc_time)

    draw.text((10, 5), f"Updated: {human_time}", fill="black", font=font)

    stations = river_doc.get("stations") or []
    x0 = 10
    y0 = 20
    gap = 15
    decimal_x = 310

    if len(stations) >= 1:
        used_h = _draw_station_graph(draw, font, stations[0], x0=x0, y0=y0)
        heights_0 = stations[0].get("heights_m") or []
        if heights_0:
            station_name_0 = str(stations[0].get("name", "")).strip()
            short_0 = (station_name_0.split() or [""])[0]
            draw.text((decimal_x - 25, y0 + 28), short_0, fill="black", font=station_font)
            _draw_large_height(draw, large_font, float(heights_0[-1]), decimal_x=decimal_x, y=y0 + 48)
        y0 = y0 + used_h + gap

    if len(stations) >= 2:
        _draw_station_graph(draw, font, stations[1], x0=x0, y0=y0)
        heights_1 = stations[1].get("heights_m") or []
        if heights_1:
            station_name_1 = str(stations[1].get("name", "")).strip()
            short_1 = (station_name_1.split() or [""])[0]
            draw.text((decimal_x - 25, y0 + 28), short_1, fill="black", font=station_font)
            _draw_large_height(draw, large_font, float(heights_1[-1]), decimal_x=decimal_x, y=y0 + 48)

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
