import csv
import re
import sys
from pathlib import Path

import gpxpy


def _safe_id(raw: str, index: int) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "", raw) or f"row_{index}"


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "gpx-data"
    input_path = data_dir / "hikr-raw-data" / "gpx-tracks-from-hikr.org.csv"
    output_dir = data_dir / "gpx-raw"
    formatted_dir = data_dir / "gpx-formatted"
    output_dir.mkdir(parents=True, exist_ok=True)
    formatted_dir.mkdir(parents=True, exist_ok=True)

    for existing in output_dir.glob("*.gpx"):
        existing.unlink()
    for existing in formatted_dir.glob("*.gpx"):
        existing.unlink()

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    processed = 0
    with input_path.open("r", encoding="utf-8", newline="") as handle:
        for index, row in enumerate(csv.DictReader(handle), start=1):
            gpx_text = row.get("gpx")
            if gpx_text:
                file_id = _safe_id(row.get("_id", ""), index)
                (output_dir / f"{file_id}.gpx").write_text(gpx_text, encoding="utf-8")
                try:
                    formatted_text = gpxpy.parse(gpx_text).to_xml(prettyprint=True)
                except Exception:
                    formatted_text = gpx_text
                (formatted_dir / f"{file_id}.gpx").write_text(
                    formatted_text, encoding="utf-8"
                )
                processed += 1
                if processed % 1000 == 0:
                    print(f"{processed} tracks processed...")

    print(f"Wrote {processed} GPX files to {formatted_dir}.")


if __name__ == "__main__":
    main()
