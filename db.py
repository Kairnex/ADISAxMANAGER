from pymongo import MongoClient
from config import MONGO_URI

client = MongoClient(MONGO_URI)
db = client['edit_guard_bot']
auth_col = db['authorized_users']
warnings_col = db['user_warnings']
