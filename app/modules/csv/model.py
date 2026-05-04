from app.extensions.db import mongo

def save_data(data):
    if data:
        mongo.db.properties.insert_many(data)

def get_all_data():
    return list(mongo.db.properties.find({}, {"_id": 0}))

def save_classified(data):
    if data:
        mongo.db.properties_classified.insert_many(data)

def get_stats_by_city():
    pipeline = [
        {
            "$group": {
                "_id": "$ubicacion.ciudad",
                "avg_price": {"$avg": "$precio"},
                "total": {"$sum": 1}
            }
        }
    ]

    return list(mongo.db.properties.aggregate(pipeline))

def get_sample_data(limit=20):
    return list(
        mongo.db.properties.find({}, {"_id": 0}).limit(limit)
    )


def save_normalized(data):
    if data:
        mongo.db.properties_normalized.insert_many(data)

def find_duplicates():
    pipeline = [
        {
            "$group": {
                "_id": {
                    "precio": "$precio",
                    "area": "$area_construida",
                    "ciudad": "$ubicacion.ciudad"
                },
                "count": {"$sum": 1},
                "docs": {"$push": "$$ROOT"}
            }
        },
        {
            "$match": {
                "count": {"$gt": 1}
            }
        }
    ]

    return list(mongo.db.properties.aggregate(pipeline))

def delete_by_ids(ids):
    if not ids:
        return 0

    result = mongo.db.properties.delete_many({
        "_id": {"$in": ids}
    })

    return result.deleted_count

def save_clean_data(data):
    if data:
        mongo.db.properties_clean.insert_many(data)