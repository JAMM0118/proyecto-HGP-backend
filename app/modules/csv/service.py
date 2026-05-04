import pandas as pd
from app.modules.csv.processor import analyze_quality, classify_property_type, clean_record, normalize_record, transform_to_star_schema
from .model import delete_by_ids, find_duplicates, delete_by_ids, get_all_data, get_sample_data, get_stats_by_city, save_classified, save_clean_data, save_data, save_normalized

def process_and_save(file):
    df = pd.read_csv(file)

    data = transform_to_star_schema(df)

    save_data(data)

    return {
        "rows": len(data),
        "message": "Datos procesados y guardados exitosamente",
        "preview": data[:3]
    }

    
def get_by_city_stats():
    return get_stats_by_city()


def preview_normalization(limit=20):
    data = get_sample_data(limit)

    result = []

    for doc in data:
        normalized = normalize_record(doc)

        result.append({
            "before": doc,
            "after": normalized
        })

    return result

def normalize_and_store():
    data = get_all_data()

    normalized_docs = []

    for doc in data:
        normalized_docs.append(normalize_record(doc))

    save_normalized(normalized_docs)

    return {
        "message": "Datos normalizados guardados",
        "count": len(normalized_docs)
    }


def delete_duplicates():
    duplicates = find_duplicates()

    ids_to_delete = []

    for group in duplicates:
        docs = group["docs"]

        # dejamos el primero, eliminamos el resto
        for doc in docs[1:]:
            ids_to_delete.append(doc["_id"])

    deleted_count = delete_by_ids(ids_to_delete)

    return {
        "duplicates_groups": len(duplicates),
        "deleted_records": deleted_count
    }



def clean_dataset():
    data = get_all_data()

    cleaned = []
    removed = 0

    for doc in data:
        result = clean_record(doc)

        if result is None:
            removed += 1
        else:
            cleaned.append(result)

    save_clean_data(cleaned)

    return {
        "original_records": len(data),
        "clean_records": len(cleaned),
        "removed_records": removed
    }


def classify_all_properties():
    data = get_all_data()

    classified = []

    for doc in data:
        new_doc = doc.copy()

        tipo = doc.get("propiedad", {}).get("tipo_propiedad", "")

        new_doc["propiedad"]["tipo_clasificado"] = classify_property_type(tipo)

        classified.append(new_doc)

    save_classified(classified)

    return {
        "total_processed": len(classified),
        "message": "Clasificación completada"
    }

def analyze_data_quality():
    data = get_all_data()

    result = analyze_quality(data)

    return result