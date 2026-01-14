import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

from dotenv import load_dotenv
from pymongo import MongoClient

import gpxpy

def to_document(gpx_dir, item):
    try:
        gpx_path = gpx_dir / item["gpx_filename"]
        gpx = gpxpy.parse(gpx_path.read_text(encoding="UTF-8"))
        doc = dict(item)
        doc.update(
            {
                "min_elevation": gpx.get_elevation_extremes()[0],
                "max_elevation": gpx.get_elevation_extremes()[1],
                "uphill": gpx.get_uphill_downhill()[0],
                "downhill": gpx.get_uphill_downhill()[1],
                "max_speed": gpx.get_moving_data().max_speed,
                "length_2d": gpx.length_2d(),
                "length_3d": gpx.length_3d(),
                "moving_time": gpx.get_moving_data().moving_time,
            }
        )
        return doc

    except Exception as e:
        print(f"Could not read {item.get('gpx_filename')}", e)
        return None


class JsonLinesImporter:
    def __init__(
        self,
        file,
        gpx_dir,
        mongo_uri,
        batch_size=200,
        db="tracks",
    ):
        self.file = file
        self.gpx_dir = gpx_dir
        self.batch_size = batch_size
        self.client = MongoClient(mongo_uri)
        self.db = db
        self.collection = "tracks"

    def read_lines(self):
        with open(self.file, encoding='UTF-8') as f:
            batch = []
            for line in f:
                batch.append(json.loads(line))
                if len(batch) == self.batch_size:
                    yield batch
                    batch.clear()
            yield batch

    def save_to_mongodb(self):
        db = self.client[self.db]
        collection = db[self.collection]
        collection.drop()
        processed = 0
        for idx, batch in enumerate(self.read_lines()):
            documents = self.prepare_documents(batch)
            if documents:
                collection.insert_many(documents)
                processed += len(documents)
            print(f"inserting batch {idx} ({processed} tracks processed)")

    def prepare_documents(self, batch):
        documents = []
        with ProcessPoolExecutor() as executor:
            for document in executor.map(to_document, [self.gpx_dir] * len(batch), batch):
                if document is not None:
                    documents.append(document)
        return documents


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', help="input file in JSON Lines format")
    args = parser.parse_args()
    env_path = Path(__file__).resolve().parent.parent / ".env"
    load_dotenv(env_path, override=True)
    mongo_uri = os.getenv("MONGO_DB_CONNECTION_STRING")
    if not mongo_uri:
        raise SystemExit(
            "Missing MongoDB URI. Set MONGO_DB_CONNECTION_STRING in .env or in the environment."
        )
    base_dir = Path(__file__).resolve().parent / "gpx-data"
    input_path = Path(args.input) if args.input else base_dir / "gpx-metadata" / "tracks.jl"
    gpx_dir = base_dir / "gpx-collected-curated"
    importer = JsonLinesImporter(input_path, gpx_dir, mongo_uri=mongo_uri)
    importer.save_to_mongodb()
