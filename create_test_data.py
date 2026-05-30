from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["mydb"]

db.properties_clean.delete_many({})

sample_data = [
    {
        "precio": 180000000,
        "area_construida": 60,
        "habitaciones": 2,
        "banos": 1,
        "ubicacion": {
            "ciudad": "cali"
        },
        "propiedad": {
            "tipo_propiedad": "apartamento"
        }
    },
    {
        "precio": 250000000,
        "area_construida": 80,
        "habitaciones": 3,
        "banos": 2,
        "ubicacion": {
            "ciudad": "cali"
        },
        "propiedad": {
            "tipo_propiedad": "apartamento"
        }
    },
    {
        "precio": 420000000,
        "area_construida": 120,
        "habitaciones": 4,
        "banos": 3,
        "ubicacion": {
            "ciudad": "bogota"
        },
        "propiedad": {
            "tipo_propiedad": "casa"
        }
    },
    {
        "precio": 600000000,
        "area_construida": 180,
        "habitaciones": 5,
        "banos": 4,
        "ubicacion": {
            "ciudad": "bogota"
        },
        "propiedad": {
            "tipo_propiedad": "casa"
        }
    },
    {
        "precio": 300000000,
        "area_construida": 100,
        "habitaciones": 3,
        "banos": 2,
        "ubicacion": {
            "ciudad": "medellin"
        },
        "propiedad": {
            "tipo_propiedad": "apartamento"
        }
    }
]

db.properties_clean.insert_many(sample_data)

print("Datos de prueba insertados")