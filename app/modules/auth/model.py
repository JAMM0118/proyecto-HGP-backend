from app.extensions.db import mongo


def find_user_by_email(email):
    return mongo.db.users.find_one({"email": email})


def create_user(user):
    return mongo.db.users.insert_one(user).inserted_id
