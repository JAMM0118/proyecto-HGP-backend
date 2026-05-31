from app.extensions.db import mongo

def get_training_data():
    return list(
        mongo.db.properties_clean.find({}, {"_id": 0})
    )

def save_prediction(data):
    mongo.db.property_predictions.insert_one(data)

def get_predictions_history(limit=100):
    return list(
        mongo.db.property_predictions.find({}, {"_id": 0})
        .sort("fecha", -1)
        .limit(limit)
    )