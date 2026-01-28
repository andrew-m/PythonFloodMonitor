import io
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as e:
    raise ImportError(
        "Pillow (PIL) is required to render PNGs. Ensure the Lambda has the Pillow layer attached."
    ) from e


def render_latest_png(river_doc: dict) -> bytes:
    img = Image.new("RGB", (400, 300), "white")
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()

    utc_time = river_doc.get("utc_time", "")
    try:
        dt = datetime.fromisoformat(utc_time.replace("Z", "+00:00"))
        human_time = dt.strftime("%H:%M %a %d %b %Y")
    except Exception:
        human_time = str(utc_time)

    draw.text((10, 10), "Fletcher", fill="black", font=font)
    draw.text((10, 30), f"Updated: {human_time}", fill="black", font=font)

    stations = river_doc.get("stations") or []
    if stations:
        station = stations[0]
        heights = station.get("heights_m") or []
        y_axis_top_m = station.get("y_axis_top_m")
        first_ts = station.get("first_timestamp_utc", "")
        last_ts = station.get("last_timestamp_utc", "")

        x0 = 10
        graph_width = 200
        graph_height = 100
        base_y = 220
        top_y = base_y - graph_height
        x_axis_end = x0 + graph_width

        draw.text((10, 55), str(station.get("name", "")), fill="black", font=font)

        draw.line([(x0, base_y), (x_axis_end, base_y)], fill="black", width=1)
        draw.line([(x0, base_y), (x0, top_y)], fill="black", width=1)

        try:
            first_dt = datetime.fromisoformat(str(first_ts).replace("Z", "+00:00"))
            first_label = first_dt.strftime("%H:%M %d %b")
        except Exception:
            first_label = str(first_ts)

        try:
            last_dt = datetime.fromisoformat(str(last_ts).replace("Z", "+00:00"))
            last_label = last_dt.strftime("%H:%M %d %b")
        except Exception:
            last_label = str(last_ts)

        draw.text((x0, base_y + 5), first_label, fill="black", font=font)
        draw.text((x_axis_end - 80, base_y + 5), last_label, fill="black", font=font)

        draw.text((x_axis_end + 5, base_y - 6), "0", fill="black", font=font)
        if isinstance(y_axis_top_m, (int, float)) and y_axis_top_m > 0:
            draw.text((x_axis_end + 5, top_y - 6), f"{y_axis_top_m:g}", fill="black", font=font)

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

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
