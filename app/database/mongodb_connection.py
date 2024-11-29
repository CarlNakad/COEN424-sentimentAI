from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
mongodb_connection_str = os.environ['MONGODB_CONNECTION_STR']
mongodb_client = MongoClient(mongodb_connection_str)
db = mongodb_client.sentimentai