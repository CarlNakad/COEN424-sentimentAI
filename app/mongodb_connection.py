from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

mongodb_connection_str = os.environ['MONGODB_CONNECTION_STR']

mongodb_client = MongoClient(mongodb_connection_str)

db = mongodb_client.sentimentai