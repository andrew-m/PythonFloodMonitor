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

    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()
