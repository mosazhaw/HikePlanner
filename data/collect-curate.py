import csv
import json
import re
import shutil
import sys
from pathlib import Path

import gpxpy


def _safe_id(raw: str, index: int) -> str:
    return re.sub(r"[^A-Za-z0-9_-]+", "", raw) or f"row_{index}"


def _has_points(gpx: gpxpy.gpx.GPX) -> bool:
    for track in gpx.tracks:
        for segment in track.segments:
            if segment.points:
                return True
    for route in gpx.routes:
        if route.points:
            return True
    return False


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data_dir = base_dir / "gpx-data"
    input_path = data_dir / "hikr-raw-data" / "gpx-tracks-from-hikr.org.csv"
    output_dir = data_dir / "gpx-collected-curated"
    metadata_dir = data_dir / "gpx-metadata"
    raw_dir = data_dir / "gpx-raw"
    metadata_path = metadata_dir / "tracks.jl"

    if output_dir.exists():
        shutil.rmtree(output_dir)
    if metadata_dir.exists():
        shutil.rmtree(metadata_dir)
    if raw_dir.exists():
        shutil.rmtree(raw_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    metadata_dir.mkdir(parents=True, exist_ok=True)

    csv.field_size_limit(min(sys.maxsize, 2**31 - 1))

    kept = 0
    skipped_empty = 0
    skipped_invalid = 0

    with input_path.open("r", encoding="utf-8", newline="") as handle:
        with metadata_path.open("w", encoding="utf-8", newline="\n") as meta_handle:
            for index, row in enumerate(csv.DictReader(handle), start=1):
                gpx_text = row.get("gpx")
                if not gpx_text:
                    continue

                try:
                    gpx = gpxpy.parse(gpx_text)
                except Exception:
                    skipped_invalid += 1
                    continue

                if not _has_points(gpx):
                    skipped_empty += 1
                    continue

                file_id = _safe_id(row.get("_id", ""), index)
                filename = f"{file_id}.gpx"
                (output_dir / filename).write_text(
                    gpx.to_xml(prettyprint=True), encoding="utf-8"
                )
                row_meta = {k: v for k, v in row.items() if k != "gpx"}
                row_meta["gpx_filename"] = filename
                meta_handle.write(json.dumps(row_meta, ensure_ascii=True) + "\n")
                kept += 1

                if kept % 1000 == 0:
                    print(f"{kept} tracks processed...")

    print(
        f"Wrote {kept} GPX files to {output_dir}. "
        f"Skipped empty: {skipped_empty}, invalid: {skipped_invalid}."
    )


if __name__ == "__main__":
    main()
