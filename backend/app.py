import datetime
import os
import pickle
import shutil
from pathlib import Path

from dotenv import load_dotenv
import pandas as pd
from azure.storage.blob import BlobServiceClient
from flask import Flask, jsonify, request, send_file
from flask_cors import CORS

ENV_STORAGE_KEY = "AZURE_STORAGE_CONNECTION_STRING"
MODEL_CONTAINER_PREFIX = "hikeplanner-model"

# init app, load model from storage
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path, override=True)
print("*** Load Model from Blob Storage ***")
if ENV_STORAGE_KEY in os.environ:
    azureStorageConnectionString = os.environ[ENV_STORAGE_KEY]
    blob_service_client = BlobServiceClient.from_connection_string(azureStorageConnectionString)

    containers = blob_service_client.list_containers(include_metadata=True)
    suffix = max(
        int(container.name.split("-")[-1])
        for container in containers
        if container.name.startswith(MODEL_CONTAINER_PREFIX)
    )
    model_folder = f"{MODEL_CONTAINER_PREFIX}-{suffix}"
    print(f"using version {model_folder}")
    
    container_client = blob_service_client.get_container_client(model_folder)
    blob_list = list(container_client.list_blobs())

    # Download all blobs to a clean local folder
    local_model_dir = Path("./model")
    if local_model_dir.exists():
        shutil.rmtree(local_model_dir)
    local_model_dir.mkdir(parents=True, exist_ok=True)
    for blob in blob_list:
        download_file_path = local_model_dir / blob.name
        print(f"downloading blob to {download_file_path.resolve()}")
        with open(file=download_file_path, mode="wb") as download_file:
            download_file.write(container_client.download_blob(blob.name).readall())

else:
    print("CANNOT ACCESS AZURE BLOB STORAGE - Please set AZURE_STORAGE_CONNECTION_STRING. Current env: ")
    print(os.environ)

file_path = Path(".", "model", "GradientBoostingRegressor.pkl")
with open(file_path, 'rb') as fid:
    model = pickle.load(fid)

def din33466(uphill, downhill, distance):
    km = distance / 1000.0
    vertical = downhill / 500.0 + uphill / 300.0
    horizontal = km / 4.0
    return 3600.0 * (min(vertical, horizontal) / 2 + max(vertical, horizontal))

def sac(uphill, downhill, distance):
    km = distance / 1000.0
    return 3600.0 * (uphill/400.0 + km /4.0)

def timedelta_minutes(seconds):
    rounded_minutes = int(round(seconds / 60.0))
    return str(datetime.timedelta(minutes=rounded_minutes))

print("\n*** Flask Backend ***")
app = Flask(__name__)
cors = CORS(app)
app = Flask(__name__, static_url_path='/', static_folder='../frontend/build')

@app.route("/")
def indexPage():
     return send_file("../frontend/build/index.html")  

@app.route("/api/predict")
def hello_world():
    downhill = request.args.get('downhill', default = 0, type = int)
    uphill = request.args.get('uphill', default = 0, type = int)
    length = request.args.get('length', default = 0, type = int)

    demoinput = [[downhill,uphill,length,0]]
    demodf = pd.DataFrame(columns=['downhill', 'uphill', 'length_3d', 'max_elevation'], data=demoinput)
    demooutput = model.predict(demodf)
    time = demooutput[0]

    return jsonify({
        'time': timedelta_minutes(time),
        'din33466': timedelta_minutes(din33466(uphill=uphill, downhill=downhill, distance=length)),
        'sac': timedelta_minutes(sac(uphill=uphill, downhill=downhill, distance=length))
        })
