import argparse
import json
import os
import sys


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--out-dir", default=".")
    args = parser.parse_args()

    repo_root = os.path.dirname(os.path.abspath(__file__))
    lambda_dir = os.path.join(repo_root, "lambda")
    sys.path.insert(0, lambda_dir)

    import river_config
    import river_data
    import render_image

    payload = river_data.build_river_level_document(river_config.STATIONS, threshold=200)

    out_dir = os.path.abspath(args.out_dir)
    os.makedirs(out_dir, exist_ok=True)

    json_path = os.path.join(out_dir, "latest.json")
    png_path = os.path.join(out_dir, "latest.png")
    bin_path = os.path.join(out_dir, "latest.bin")

    with open(json_path, "wb") as f:
        f.write(json.dumps(payload, separators=(",", ":")).encode("utf-8"))

    png_bytes = render_image.render_latest_png(payload)
    with open(png_path, "wb") as f:
        f.write(png_bytes)

    bin_bytes = render_image.render_latest_mono_hlsb_black(payload)
    with open(bin_path, "wb") as f:
        f.write(bin_bytes)

    print(json_path)
    print(png_path)
    print(bin_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
