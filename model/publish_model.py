# https://learn.microsoft.com/en-us/azure/storage/blobs/storage-quickstart-blobs-python?tabs=managed-identity%2Croles-azure-portal%2Csign-in-azure-cli
# Erlaubnis auf eigenes Konto geben :-)

import os
from azure.storage.blob import BlobServiceClient
from pathlib import Path

from dotenv import load_dotenv

try:
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path, override=True)
    conn_str = os.getenv("AZURE_STORAGE_CONNECTION_STRING")
    if not conn_str:
        raise SystemExit(
            "Missing AZURE_STORAGE_CONNECTION_STRING in .env or in the environment."
        )

    blob_service_client = BlobServiceClient.from_connection_string(conn_str)

    suffix = 0
    for container in blob_service_client.list_containers():
        name = container["name"]
        if name.startswith("hikeplanner-model-"):
            parts = name.split("-")
            if len(parts) == 3 and parts[-1].isdigit():
                suffix = max(suffix, int(parts[-1]))

    suffix += 1
    container_name = f"hikeplanner-model-{suffix}"
    print(f"Using container: {container_name}")
    blob_service_client.create_container(container_name)

    local_files = ["GradientBoostingRegressor.pkl", "LinearRegression.pkl"]
    for local_file_name in local_files:
        upload_file_path = os.path.join(".", local_file_name)
        # Create a blob client using the local file name as the name for the blob
        blob_client = blob_service_client.get_blob_client(
            container=container_name, blob=local_file_name
        )
        print(f"Uploading {local_file_name}...")
        # Upload the created file
        with open(file=upload_file_path, mode="rb") as data:
            blob_client.upload_blob(data)

except Exception as ex:
    print('Exception:')
    print(ex)
    exit(1)
