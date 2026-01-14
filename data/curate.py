from pathlib import Path

import gpxpy


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
    input_dir = data_dir / "gpx-formatted"
    output_dir = data_dir / "gpx-curated"
    output_dir.mkdir(parents=True, exist_ok=True)

    for existing in output_dir.glob("*.gpx"):
        existing.unlink()

    kept = 0
    skipped_empty = 0
    skipped_invalid = 0

    for index, gpx_path in enumerate(input_dir.glob("*.gpx"), start=1):
        try:
            gpx = gpxpy.parse(gpx_path.read_text(encoding="utf-8"))
        except Exception:
            skipped_invalid += 1
            continue

        if _has_points(gpx):
            (output_dir / gpx_path.name).write_text(
                gpx.to_xml(prettyprint=True), encoding="utf-8"
            )
            kept += 1
        else:
            skipped_empty += 1

        if index % 1000 == 0:
            print(f"{index} tracks processed...")

    print(
        f"Wrote {kept} GPX files to {output_dir}. "
        f"Skipped empty: {skipped_empty}, invalid: {skipped_invalid}."
    )


if __name__ == "__main__":
    main()
