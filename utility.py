import os
import pymongo
def get_mongodb_collection():
    connection_string = f"""mongodb+srv://{os.getenv('MONGODB_USER')}:{os.getenv('MONGODB_PASSWORD')}@cluster0.i3vlvqh.mongodb.net/?retryWrites=true&w=majority"""
    client = pymongo.MongoClient(connection_string)
    database=client["youtale"]
    collection=database["signup_credebtials"]
    return collection