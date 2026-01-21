"""Upload hikr.org raw data to Azure Blob Storage using versioned containers."""

from __future__ import annotations

import os
from pathlib import Path

from azure.core.exceptions import ResourceExistsError
from azure.storage.blob import BlobServiceClient
from dotenv import load_dotenv

RAW_DIR = Path(__file__).resolve().parent / "gpx-data" / "hikr-raw-data"
RAW_CONTAINER_PREFIX = "hikeplanner-raw-data"


def _iter_files(root: Path):
    for path in root.rglob("*"):
        if path.is_file():
            yield path


def _compute_next_container(blob_service_client: BlobServiceClient) -> str:
    prefix = f"{RAW_CONTAINER_PREFIX}-"
    max_suffix = 0
    for container in blob_service_client.list_containers():
        name = container["name"]
        if name.startswith(prefix):
            suffix = name[len(prefix) :]
            if suffix.isdigit():
                max_suffix = max(max_suffix, int(suffix))
    return f"{RAW_CONTAINER_PREFIX}-{max_suffix + 1}"


def upload_raw_data() -> None:
    if not RAW_DIR.exists():
        raise SystemExit(f"Source directory not found: {RAW_DIR}")

    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path, override=True)
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise SystemExit(
            "Missing AZURE_STORAGE_CONNECTION_STRING in .env or environment."
        )

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)
    container_name = _compute_next_container(blob_service_client)
    print(f"Creating container {container_name} for this upload")
    try:
        container_client = blob_service_client.create_container(container_name)
    except ResourceExistsError:
        container_client = blob_service_client.get_container_client(container_name)

    uploaded = 0
    for path in _iter_files(RAW_DIR):
        blob_name = path.relative_to(RAW_DIR).as_posix()
        with path.open("rb") as data:
            container_client.upload_blob(blob_name, data)
        uploaded += 1
        print(f"Uploaded {path.name} -> {blob_name}")

    print(f"Uploaded {uploaded} files to container {container_name}")


if __name__ == "__main__":
    upload_raw_data()
