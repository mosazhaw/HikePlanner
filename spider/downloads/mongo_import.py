# new terminal
# cd spider/downloads
# python .\mongo_import.py -c tracks -i ../file.jl -u 'MONGO_DB_CONNECTION_STRING'

import argparse
import json
import os
from concurrent.futures import ProcessPoolExecutor

from pymongo import MongoClient

import gpxpy
import gpxpy.gpx
from pathlib import Path

def to_document(base_dir, item):
    try:
        #file_item = item["files"][0]
        # file_path = os.path.join(base_dir, "downloads", file_item['path'])
        #file_path = Path(base_dir, "downloads", file_item['path'])
        #file = open(file_path, encoding='UTF-8')
        #gpx = gpxpy.parse(file)
        #doc = {
            # "gpx": gpx.to_xml(),
         #   "min_elevation": gpx.get_elevation_extremes()[0],            
          #  "max_elevation": gpx.get_elevation_extremes()[1],
          #  "uphill": gpx.get_uphill_downhill()[0],            
          #  "downhill": gpx.get_uphill_downhill()[1],
          #  "max_speed": gpx.get_moving_data().max_speed,                        
          #  "length_2d": gpx.length_2d(),                     
          #  "length_3d": gpx.length_3d(),
          #  "moving_time": gpx.get_moving_data().moving_time,
          #  "difficulty": item["difficulty"]
        #}
        doc = {
            "title": item["title"],
            "price": item["price"],
            "last12MonthEarnings": item["last12MonthEarnings"],
            "dollarAge": item["dollarAge"]
        }
        return doc
            
    except Exception as e:
        print("Could not read {}".format(item["files"][0]), e)
        return None


class JsonLinesImporter:

    def __init__(self, file, mongo_uri, batch_size=30, db='sales', collection='sales'):
        self.file = file
        self.base_dir = os.path.dirname(file)
        self.batch_size = batch_size
        self.client = MongoClient(mongo_uri)
        self.db = db
        self.collection = collection

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
        for idx, batch in enumerate(self.read_lines()):
            print("inserting batch", idx)
            collection.insert_many(self.prepare_documents(batch))

    def prepare_documents(self, batch):
        documents = []
        with ProcessPoolExecutor() as executor:
            for document in executor.map(to_document, [self.base_dir] * len(batch), batch):
                if document is not None:
                    documents.append(document)
        return documents


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--uri', required=True, help="mongodb uri with username/password")
    parser.add_argument('-i', '--input', required=True, help="input file in JSON Lines format")
    parser.add_argument('-c', '--collection', required=True, help="name of the mongodb collection where the tracks should be stored")
    args = parser.parse_args()
    importer = JsonLinesImporter(args.input, collection=args.collection, mongo_uri=args.uri)
    importer.save_to_mongodb()
