from flask import Blueprint, request, jsonify
from app.modules.csv.model import get_sample_data
from app.modules.csv.processor import classify_property_type
from .service import  analyze_data_quality, classify_all_properties, classify_all_properties, clean_dataset, delete_duplicates, get_by_city_stats, normalize_and_store, preview_normalization, process_and_save

csv_bp = Blueprint("csv", __name__)

@csv_bp.route("/upload", methods=["POST"])
def upload_csv():
    """
    Subir archivo CSV
    ---
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Archivo CSV a subir
    responses:
      200:
        description: CSV procesado correctamente
    """
    file = request.files.get("file")

    if not file:
        return jsonify({"error": "No file"}), 400

    result = process_and_save(file)

    return jsonify(result)

@csv_bp.route("/avg-price-by-city", methods=["GET"])
def avg_price_by_city_stats():
    """
    Obtener estadísticas de precio promedio por ciudad
    ---
    responses:
      200:
        description: Estadísticas obtenidas correctamente
    """
    result = get_by_city_stats()
    return jsonify(result)

@csv_bp.route("/normalize-preview", methods=["GET"])
def normalize_preview():
    """
    Obtener vista previa de datos normalizados
    ---
    responses:
      200:
        description: Vista previa obtenida correctamente

    """
    result = preview_normalization()
    return jsonify(result)


@csv_bp.route("/normalize-save", methods=["POST"])
def normalize_and_save():
    """
    Normalizar y guardar datos
    ---
    responses:
      200:
        description: Datos normalizados y guardados correctamente
    """
    result = normalize_and_store()
    return jsonify(result)

@csv_bp.route("/remove-duplicates", methods=["DELETE"])
def remove_duplicates():
    """
    Eliminar registros duplicados
    ---
    responses:
      200:
        description: Registros duplicados eliminados correctamente
    """
    result = delete_duplicates()
    return jsonify(result)

@csv_bp.route("/clean-data", methods=["POST"])
def clean_data():
    """
    Limpiar datos (eliminar registros con datos faltantes o inconsistentes)
    ---
    responses:
      200:
        description: Datos limpiados correctamente
    """
    result = clean_dataset()
    return jsonify(result)


@csv_bp.route("/data-quality", methods=["GET"])
def data_quality():
    """
    Obtener estadísticas de calidad de los datos
    ---
    responses:
      200:
        description: Estadísticas de calidad obtenidas correctamente
    """
    result = analyze_data_quality()
    return jsonify(result)


@csv_bp.route("/classify-properties", methods=["POST"])
def classify_properties():
    """
    Clasificar propiedades en categorías (bajo, medio, alto)
    ---
    responses:
      200:
        description: Propiedades clasificadas correctamente 
    """
    result = classify_all_properties()
    return jsonify(result)

@csv_bp.route("/classify-preview", methods=["GET"])
def classify_preview():
    """
    Obtener vista previa de clasificación de tipo de propiedad
    ---
    responses:
      200:
        description: Vista previa obtenida correctamente
    """
    data = get_sample_data(1200)

    result = []

    for doc in data:
        tipo = doc.get("propiedad", {}).get("tipo_propiedad", "")

        result.append({
            "original": tipo,
            "clasificado": classify_property_type(tipo)
        })

    return jsonify(result)