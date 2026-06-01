from collections import defaultdict

import pandas as pd
import re

def clean_price(value):
    if value is None:
        return None

    value = str(value)

    # quitar $, puntos, comas, texto
    value = re.sub(r"[^\d]", "", value)

    return int(value) if value else None


def clean_area(value):
    if value is None:
        return None

    value = str(value).lower()

    # detectar m2 o metros
    value = re.sub(r"[^\d.]", "", value)

    return float(value) if value else None


def normalize_record(doc):

    normalized = doc.copy()

    # 🔹 precio
    if "precio" in doc:
        normalized["precio"] = clean_price(doc["precio"])

    # 🔹 area
    if "area_construida" in doc:
        normalized["area_construida"] = clean_area(doc["area_construida"])

    return normalized

import pandas as pd


def transform_to_star_schema(df: pd.DataFrame):

    df = df.copy()

    df.rename(columns={
        "Fecha Actualizacion": "fecha_actualizacion",
        "ID Propiedad": "id_propiedad",
        "Link Propiedad": "link_propiedad",
        "Tipo Propiedad": "tipo_propiedad",
        "Tipo Operacion": "tipo_operacion",
        "Link Google Maps": "link_google_maps",
        "Ubicacion Principal": "ubicacion_principal",
        "Piso N": "piso_n",
        "Area Construida": "area_construida",
        "Estado Construccion": "estado_construccion"
    }, inplace=True)

    df["fecha_actualizacion"] = pd.to_datetime(
        df["fecha_actualizacion"],
        errors="coerce"
    )

    text_columns = [
        "Ciudad",
        "Localidad",
        "Zona",
        "Region",
        "tipo_propiedad",
        "estado_construccion",
        "Antiguedad_Categoria"
    ]

    for col in text_columns:
        df[col] = (
            df[col]
            .fillna("")
            .astype(str)
            .str.lower()
            .str.strip()
        )

    docs = []

    for row in df.itertuples(index=False):
        
        doc = {
            # HECHOS
            "precio": (
                float(row.Precio)
                if pd.notna(row.Precio)
                else None
            ),

            "area_construida": (
                float(row.area_construida)
                if pd.notna(row.area_construida)
                else None
            ),

            "habitaciones": (
                int(row.Habitaciones)
                if pd.notna(row.Habitaciones)
                else None
            ),

            "banos": (
                int(row.Banos)
                if pd.notna(row.Banos)
                else None
            ),

            "garages": (
                int(row.Garages)
                if pd.notna(row.Garages)
                else None
            ),

            "estrato": (
                int(row.Estrato)
                if pd.notna(row.Estrato)
                else None
            ),

            # DIMENSIÓN UBICACIÓN
            "ubicacion": {
                "ciudad": row.Ciudad,
                "localidad": row.Localidad,
                "zona": row.Zona,
                "region": row.Region,
                "barrio": row.ubicacion_principal,
                "direccion": row.Direccion

            },

            # DIMENSIÓN PROPIEDAD
            "propiedad": {
                "titulo" : row.Titulo,
                "tipo_operacion": row.tipo_operacion,
                "tipo_propiedad": row.tipo_propiedad,
                "estado_construccion": row.estado_construccion,
                "antiguedad_categoria": row.Antiguedad_Categoria,
                "antiguedad": row.Antiguedad if pd.notna(row.Antiguedad) else None
            }
        }

        fecha = row.fecha_actualizacion

        if pd.notna(fecha):
            doc["tiempo"] = {
                "fecha": fecha.to_pydatetime(),
                "anio": fecha.year,
                "mes": fecha.month
            }

        docs.append(doc)

    return docs

def clean_record(doc):

    # ❌ eliminar registros inválidos (ejemplo)
    if not doc.get("precio") or doc.get("precio") == 0:
        return None

    if not doc.get("ubicacion", {}).get("ciudad"):
        return None

    cleaned = doc.copy()

    # 🔹 reemplazar nulos

    # habitaciones
    if cleaned.get("habitaciones") is None:
        cleaned["habitaciones"] = 0

    # baños
    if cleaned.get("banos") is None:
        cleaned["banos"] = 0

    # área
    if cleaned.get("area_construida") is None:
        cleaned["area_construida"] = 0

    # estrato
    if cleaned.get("estrato") is None:
        cleaned["estrato"] = 3  # valor promedio típico

    # texto
    if not cleaned.get("propiedad", {}).get("tipo_propiedad"):
        cleaned["propiedad"]["tipo_propiedad"] = "desconocido"

    return cleaned

def classify_property_type(value):

    if not value:
        return "otro"

    value = value.lower().strip()

    # 🔥 reglas
    if "apart" in value or "apto" in value:
        return "apartamento"

    if "casa" in value:
        return "casa"

    if "lote" in value or "terreno" in value:
        return "lote"

    if "oficina" in value:
        return "oficina"

    if "local" in value:
        return "local"

    return "otro"


def analyze_quality(data):

    null_counts = defaultdict(int)
    total = len(data)

    out_of_range = {
        "precio_negativo": 0,
        "area_invalida": 0,
        "habitaciones_negativas": 0
    }

    for doc in data:

        # 🔹 detectar nulos
        for key, value in doc.items():

            if isinstance(value, dict):
                for sub_key, sub_val in value.items():
                    if sub_val is None or sub_val == "":
                        null_counts[f"{key}.{sub_key}"] += 1
            else:
                if value is None or value == "":
                    null_counts[key] += 1

        # 🔥 detectar fuera de rango

        # precio negativo
        if doc.get("precio") is not None and doc["precio"] < 0:
            out_of_range["precio_negativo"] += 1

        # area inválida
        if doc.get("area_construida") is not None and doc["area_construida"] <= 0:
            out_of_range["area_invalida"] += 1

        # habitaciones negativas
        if doc.get("habitaciones") is not None and doc["habitaciones"] < 0:
            out_of_range["habitaciones_negativas"] += 1

    # 🔥 resumen final
    summary = {
        "total_records": total,
        "nulls_by_column": dict(null_counts),
        "out_of_range": out_of_range
    }

    return summary