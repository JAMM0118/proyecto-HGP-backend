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
    user["role"] = user.get("role", "invitado")  # Default role
    return mongo.db.users.insert_one(user).inserted_id

def update_user_last_login(user_id):
    mongo.db.users.update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"last_login": datetime.utcnow()}}
    )

def add_token_to_blacklist(token):
    """Add token to blacklist collection for logout"""
    mongo.db.token_blacklist.insert_one({
        "token": token,
        "created_at": datetime.utcnow()
    })

def is_token_blacklisted(token):
    """Check if token is in blacklist"""
    return mongo.db.token_blacklist.find_one({"token": token}) is not None
