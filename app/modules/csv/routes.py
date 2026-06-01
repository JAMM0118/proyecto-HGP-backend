from flask import Blueprint, request, jsonify
from app.modules.csv.model import get_sample_data
from app.modules.csv.processor import classify_property_type
from .service import  analyze_data_quality, classify_all_properties, classify_all_properties, clean_dataset, delete_duplicates, get_area_comparison_stats, get_by_city_stats, get_correlation_matrix_data, get_market_trend_stats, get_price_distribution_stats, get_price_vs_area_stats, get_price_vs_bedrooms_stats, get_properties_page_data, get_property_analysis_stats, get_top_barrio_growth_stats, get_top_cities_stats, normalize_and_store, preview_normalization, process_and_save

csv_bp = Blueprint("csv", __name__)

@csv_bp.route("/upload", methods=["POST"])
def upload_csv():
    """
    Subir archivo CSV
    ---
    tags:
      - CSV
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
    tags:
      - CSV 
    responses:
      200:
        description: Estadísticas obtenidas correctamente
    """
    result = get_by_city_stats()
    return jsonify(result)


@csv_bp.route("/property-analysis-stats", methods=["GET"])
def property_analysis_stats():
    """
    Obtener métricas generales de propiedades analizadas
    ---
    tags:
      - CSV
    responses:
      200:
        description: Métricas generales obtenidas correctamente
    """
    result = get_property_analysis_stats()
    return jsonify(result)


@csv_bp.route("/price-distribution-stats", methods=["GET"])
def price_distribution_stats():
    """
    Obtener la distribución de propiedades por rangos de precio
    ---
    tags:
      - CSV
    responses:
      200:
        description: Distribución de precios obtenida correctamente
    """
    result = get_price_distribution_stats()
    return jsonify(result)


@csv_bp.route("/market-trend-stats", methods=["GET"])
def market_trend_stats():
    """
    Obtener la tendencia del mercado por año con enero y diciembre
    ---
    tags:
      - CSV
    responses:
      200:
        description: Tendencia del mercado obtenida correctamente
    """
    result = get_market_trend_stats()
    return jsonify(result)


@csv_bp.route("/area-comparison-stats", methods=["GET"])
def area_comparison_stats():
    """
    Comparar propiedades con area_construida mayor y menor a 100
    ---
    tags:
      - CSV
    responses:
      200:
        description: Comparación por área obtenida correctamente
    """
    result = get_area_comparison_stats()
    return jsonify(result)


@csv_bp.route("/price-vs-area-stats", methods=["GET"])
def price_vs_area_stats():
    """
    Comparar el precio respecto al area_construida
    ---
    tags:
      - CSV
    responses:
      200:
        description: Comparación precio vs área obtenida correctamente
    """
    result = get_price_vs_area_stats()
    return jsonify(result)


@csv_bp.route("/price-vs-bedrooms-stats", methods=["GET"])
def price_vs_bedrooms_stats():
    """
    Comparar el precio respecto al numero de habitaciones
    ---
    tags:
      - CSV
    responses:
      200:
        description: Comparación precio vs habitaciones obtenida correctamente
    """
    result = get_price_vs_bedrooms_stats()
    return jsonify(result)


@csv_bp.route("/correlation-matrix-data", methods=["GET"])
def correlation_matrix_data():
    """
    Obtener datos listos para generar una matriz de correlacion (Precio, Habitaciones, Baños, Area)
    ---
    tags:
      - CSV
    responses:
      200:
        description: Datos para matriz de correlacion obtenidos correctamente
    """
    result = get_correlation_matrix_data()
    return jsonify(result)


@csv_bp.route("/top-cities-stats", methods=["GET"])
def top_cities_stats():
    """
    Obtener las 4 ciudades con mejores métricas de propiedades
    ---
    tags:
      - CSV
    responses:
      200:
        description: Estadísticas de ciudades obtenidas correctamente
    """
    result = get_top_cities_stats(limit=4)
    return jsonify(result)


@csv_bp.route("/top-barrio-growth-stats", methods=["GET"])
def top_barrio_growth_stats():
    """
    Obtener los 4 barrios con mayor crecimiento porcentual en precio
    ---
    tags:
      - CSV
    responses:
      200:
        description: Estadísticas de barrios obtenidas correctamente
    """
    result = get_top_barrio_growth_stats(limit=4)
    return jsonify(result)

@csv_bp.route("/normalize-preview", methods=["GET"])
def normalize_preview():
    """
    Obtener vista previa de datos normalizados
    ---
    tags:
      - CSV
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
    tags:
      - CSV
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
    tags:
      - CSV
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
    tags:
      - CSV
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
    tags:
      - CSV
    responses:
      200:
        description: Estadísticas de calidad obtenidas correctamente
    """
    result = analyze_data_quality()
    return jsonify(result)


@csv_bp.route("/classify-properties", methods=["GET"])
def classify_properties():
    """
    Obtener el conteo de propiedades agrupadas por tipo_propiedad
    ---
    tags:
      - CSV
    responses:
      200:
        description: Conteo de propiedades por tipo obtenido correctamente
    """
    result = classify_all_properties()
    return jsonify(result)

@csv_bp.route("/classify-preview", methods=["GET"])
def classify_preview():
    """
    Obtener vista previa de clasificación de tipo de propiedad
    ---
    tags:
      - CSV
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


@csv_bp.route("/properties", methods=["GET"])
def list_properties():
    """
    Obtener registros de properties con paginación por página
    ---
    tags:
      - CSV
    parameters:
      - name: page
        in: query
        type: integer
        required: false
        default: 1
        description: Número de página a consultar
      - name: pageSize
        in: query
        type: integer
        required: false
        default: 15
        description: Cantidad de registros por página
      - name: bedrooms
        in: query
        type: integer
        required: false
        description: Cantidad de habitaciones
      - name: bathrooms
        in: query
        type: integer
        required: false
        description: Cantidad de baños
      - name: minPrice
        in: query
        type: number
        required: false
        description: Precio mínimo
      - name: maxPrice
        in: query
        type: number
        required: false
        description: Precio máximo
      - name: city
        in: query
        type: string
        required: false
        description: Ciudad a filtrar
    responses:
      200:
        description: Registros obtenidos correctamente
    """
    try:
        page = int(request.args.get("page", 1))
        page_size = int(request.args.get("pageSize", 15))
        bedrooms = request.args.get("bedrooms")
        bathrooms = request.args.get("bathrooms")
        min_price = request.args.get("minPrice")
        max_price = request.args.get("maxPrice")
    except ValueError:
        return jsonify({"error": "page y pageSize deben ser enteros"}), 400

    if page <= 0 or page_size <= 0:
        return jsonify({"error": "page y pageSize deben ser mayores que 0"}), 400

    filters = {}

    if bedrooms is not None:
        try:
            filters["habitaciones"] = int(bedrooms)
        except ValueError:
          return jsonify({"error": "bedrooms debe ser un entero"}), 400

    if bathrooms is not None:
        try:
            filters["banos"] = int(bathrooms)
        except ValueError:
          return jsonify({"error": "bathrooms debe ser un entero"}), 400

    price_filter = {}

    if min_price is not None:
        try:
            price_filter["$gte"] = float(min_price)
        except ValueError:
          return jsonify({"error": "minPrice debe ser un número"}), 400

    if max_price is not None:
        try:
            price_filter["$lte"] = float(max_price)
        except ValueError:
          return jsonify({"error": "maxPrice debe ser un número"}), 400

    if price_filter:
        filters["precio"] = price_filter

    city = request.args.get("city")
    if city:
        filters["ubicacion.ciudad"] = city.strip().lower()

    result = get_properties_page_data(page=page, page_size=page_size, filters=filters)

    return jsonify(result)