from app.extensions.db import mongo
from datetime import datetime
from bson import ObjectId

def find_user_by_email(email):
    return mongo.db.users.find_one({"email": email})

def find_user_by_id(user_id):
    return mongo.db.users.find_one({"_id": ObjectId(user_id)})

def create_user(user):
    user["created_at"] = datetime.utcnow()
    user["updated_at"] = datetime.utcnow()
    user["is_active"] = True
    return mongo.db.users.insert_one(user).inserted_id

def update_user_last_login(user_id):
    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login": datetime.utcnow()}}
    )
