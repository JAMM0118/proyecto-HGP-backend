from collections import Counter, defaultdict
import statistics

import pandas as pd
from app.modules.csv.processor import analyze_quality, classify_property_type, clean_record, normalize_record, transform_to_star_schema
from .model import count_properties, delete_by_ids, find_duplicates, delete_by_ids, get_all_data, get_properties_page, get_sample_data, get_stats_by_city, save_clean_data, save_data, save_normalized

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


def get_property_analysis_stats():
    data = get_all_data()

    total_properties = len(data)

    valid_prices = []
    price_per_m2_values = []

    for doc in data:
        price = doc.get("precio")
        area = doc.get("area_construida")

        if isinstance(price, (int, float)):
            valid_prices.append(float(price))

        if isinstance(price, (int, float)) and isinstance(area, (int, float)) and area > 0:
            price_per_m2_values.append(float(price) / float(area))

    average_property_value = (
        sum(valid_prices) / len(valid_prices)
        if valid_prices
        else 0
    )

    average_price_per_m2 = (
        sum(price_per_m2_values) / len(price_per_m2_values)
        if price_per_m2_values
        else 0
    )

    return {
        "total_propiedades_analizadas": total_properties,
        "valor_promedio_de_propiedad": round(average_property_value, 2),
        "precio_promedio_por_m2": round(average_price_per_m2, 2),
    }


def get_top_cities_stats(limit=4):
    data = get_all_data()

    city_stats = defaultdict(lambda: {
        "total_properties": 0,
        "price_sum": 0.0,
        "price_count": 0,
        "year_counts": defaultdict(int),
    })

    for doc in data:
        city = doc.get("ubicacion", {}).get("ciudad")
        if not city:
            continue

        city = str(city).strip().lower()
        price = doc.get("precio")
        year = doc.get("tiempo", {}).get("anio")

        stats = city_stats[city]
        stats["total_properties"] += 1

        if isinstance(price, (int, float)):
            stats["price_sum"] += float(price)
            stats["price_count"] += 1

        if isinstance(year, int):
            stats["year_counts"][year] += 1

    ranked_cities = sorted(
        city_stats.items(),
        key=lambda item: item[1]["total_properties"],
        reverse=True,
    )[:limit]

    result = []

    for city, stats in ranked_cities:
        year_counts = stats["year_counts"]
        years = sorted(year_counts.keys())

        first_year = years[0] if years else None
        last_year = years[-1] if years else None
        first_year_count = year_counts[first_year] if first_year is not None else 0
        last_year_count = year_counts[last_year] if last_year is not None else 0

        if first_year_count > 0:
            growth_percentage = ((last_year_count - first_year_count) / first_year_count) * 100
        else:
            growth_percentage = 0

        average_price = (
            stats["price_sum"] / stats["price_count"]
            if stats["price_count"]
            else 0
        )

        result.append({
            "ciudad": city,
            "cantidad_propiedades": stats["total_properties"],
            "precio_promedio_propiedades": round(average_price, 2),
            "crecimiento_porcentual": round(growth_percentage, 2),
            "primer_anio": first_year,
            "ultimo_anio": last_year,
            "propiedades_primer_anio": first_year_count,
            "propiedades_ultimo_anio": last_year_count,
        })

    return {
        "total_ciudades_analizadas": len(city_stats),
        "top_ciudades": result,
    }


def get_top_barrio_growth_stats(limit=4):
    data = get_all_data()

    # key by barrio+ciudad to distinguish same barrio name across cities
    barrio_stats = defaultdict(lambda: {
        "price_by_year": defaultdict(list),
        "price_sum": 0.0,
        "price_count": 0,
        "barrio_name": None,
        "city_name": None,
    })

    for doc in data:
        barrio = doc.get("ubicacion", {}).get("barrio")
        city = doc.get("ubicacion", {}).get("ciudad")
        year = doc.get("tiempo", {}).get("anio")
        price = doc.get("precio")

        if not barrio or not city or not isinstance(year, int) or not isinstance(price, (int, float)):
            continue

        key = f"{str(barrio).strip().lower()}||{str(city).strip().lower()}"
        stats = barrio_stats[key]

        stats["barrio_name"] = str(barrio).strip()
        stats["city_name"] = str(city).strip()
        stats["price_by_year"][year].append(float(price))
        stats["price_sum"] += float(price)
        stats["price_count"] += 1

    ranked_barrio = []

    for key, stats in barrio_stats.items():
        year_keys = sorted(stats["price_by_year"].keys())

        if not year_keys:
            continue

        first_year = year_keys[0]
        last_year = year_keys[-1]

        first_year_avg = sum(stats["price_by_year"][first_year]) / len(stats["price_by_year"][first_year])
        last_year_avg = sum(stats["price_by_year"][last_year]) / len(stats["price_by_year"][last_year])

        if first_year_avg > 0:
            growth_percentage = ((last_year_avg - first_year_avg) / first_year_avg) * 100
        else:
            growth_percentage = 0

        average_price = (
            stats["price_sum"] / stats["price_count"]
            if stats["price_count"]
            else 0
        )

        ranked_barrio.append({
            "barrio": stats["barrio_name"],
            "ciudad": stats["city_name"],
            "crecimiento_porcentual": round(growth_percentage, 2),
            "precio_promedio": round(average_price, 2),
            "primer_anio": first_year,
            "ultimo_anio": last_year,
            "precio_promedio_primer_anio": round(first_year_avg, 2),
            "precio_promedio_ultimo_anio": round(last_year_avg, 2),
        })

    ranked_barrio.sort(key=lambda item: item["crecimiento_porcentual"], reverse=True)

    return {
        "total_barrios_analizados": len(barrio_stats),
        "top_barrios": ranked_barrio[:limit],
    }


def get_price_distribution_stats():
    data = get_all_data()

    buckets = {
        "0-200_millones": 0,
        "200-400_millones": 0,
        "400-600_millones": 0,
        "600-800_millones": 0,
        "800_millones-1_billon": 0,
        "1_billon_mas": 0,
    }

    total_valid_prices = 0

    for doc in data:
        price = doc.get("precio")

        if not isinstance(price, (int, float)):
            continue

        total_valid_prices += 1
        price_millions = float(price) / 1_000_000

        if price_millions < 200:
            buckets["0-200_millones"] += 1
        elif price_millions < 400:
            buckets["200-400_millones"] += 1
        elif price_millions < 600:
            buckets["400-600_millones"] += 1
        elif price_millions < 800:
            buckets["600-800_millones"] += 1
        elif price_millions < 1000:
            buckets["800_millones-1_billon"] += 1
        else:
            buckets["1_billon_mas"] += 1

    return {
        "total_propiedades_con_precio": total_valid_prices,
        "distribucion_precios": buckets,
    }


def get_market_trend_stats():
    data = get_all_data()

    yearly_stats = defaultdict(lambda: {
        "prices": [],
        "january_prices": [],
        "december_prices": [],
    })

    for doc in data:
        time_data = doc.get("tiempo", {})
        year = time_data.get("anio")
        month = time_data.get("mes")
        price = doc.get("precio")

        if not isinstance(year, int) or not isinstance(price, (int, float)):
            continue

        stats = yearly_stats[year]
        stats["prices"].append(float(price))

        if month == 1:
            stats["january_prices"].append(float(price))
        elif month == 12:
            stats["december_prices"].append(float(price))

    years = sorted(yearly_stats.keys())

    trend = []

    for year in years:
        stats = yearly_stats[year]

        annual_avg = (
            sum(stats["prices"]) / len(stats["prices"])
            if stats["prices"]
            else 0
        )

        january_avg = (
            sum(stats["january_prices"]) / len(stats["january_prices"])
            if stats["january_prices"]
            else None
        )

        december_avg = (
            sum(stats["december_prices"]) / len(stats["december_prices"])
            if stats["december_prices"]
            else None
        )

        trend.append({
            "anio": year,
            "precio_promedio_anual": round(annual_avg, 2),
            "enero": round(january_avg, 2) if january_avg is not None else None,
            "diciembre": round(december_avg, 2) if december_avg is not None else None,
            "cantidad_propiedades": len(stats["prices"]),
        })

    return {
        "primer_anio": years[0] if years else None,
        "ultimo_anio": years[-1] if years else None,
        "tendencia_mercado": trend,
    }


def get_area_comparison_stats():
    data = get_all_data()

    groups = {
        "mas_de_100": defaultdict(lambda: {"cantidad": 0, "total_precio": 0.0}),
        "menos_de_100": defaultdict(lambda: {"cantidad": 0, "total_precio": 0.0}),
    }

    totals = {
        "mas_de_100": {"cantidad": 0, "total_precio": 0.0},
        "menos_de_100": {"cantidad": 0, "total_precio": 0.0},
    }

    for doc in data:
        area = doc.get("area_construida")
        price = doc.get("precio")
        tipo = doc.get("propiedad", {}).get("tipo_propiedad", "desconocido")

        if not isinstance(area, (int, float)):
            continue

        if not isinstance(price, (int, float)):
            price = 0

        bucket = "mas_de_100" if float(area) > 100 else "menos_de_100"

        totals[bucket]["cantidad"] += 1
        totals[bucket]["total_precio"] += float(price)

        type_stats = groups[bucket][str(tipo).strip().lower() or "desconocido"]
        type_stats["cantidad"] += 1
        type_stats["total_precio"] += float(price)

    def serialize_group(bucket_name):
        type_breakdown = [
            {
                "tipo_propiedad": tipo,
                "cantidad": stats["cantidad"],
                "total_precio": round(stats["total_precio"], 2),
            }
            for tipo, stats in sorted(groups[bucket_name].items(), key=lambda item: item[1]["cantidad"], reverse=True)
        ]

        return {
            "cantidad": totals[bucket_name]["cantidad"],
            "total_precio": round(totals[bucket_name]["total_precio"], 2),
            "por_tipo_propiedad": type_breakdown,
        }

    return {
        "comparacion_area": {
            "mas_de_100": serialize_group("mas_de_100"),
            "menos_de_100": serialize_group("menos_de_100"),
        }
    }


def get_price_vs_area_stats():
    data = get_all_data()

    area_buckets = {
        "0-50": {"count": 0, "price_sum": 0.0, "area_sum": 0.0},
        "50-100": {"count": 0, "price_sum": 0.0, "area_sum": 0.0},
        "100-150": {"count": 0, "price_sum": 0.0, "area_sum": 0.0},
        "150-200": {"count": 0, "price_sum": 0.0, "area_sum": 0.0},
        "200+": {"count": 0, "price_sum": 0.0, "area_sum": 0.0},
    }

    for doc in data:
        area = doc.get("area_construida")
        price = doc.get("precio")

        if not isinstance(area, (int, float)) or not isinstance(price, (int, float)):
            continue

        area_value = float(area)
        price_value = float(price)

        if area_value < 50:
            bucket = "0-50"
        elif area_value < 100:
            bucket = "50-100"
        elif area_value < 150:
            bucket = "100-150"
        elif area_value < 200:
            bucket = "150-200"
        else:
            bucket = "200+"

        area_buckets[bucket]["count"] += 1
        area_buckets[bucket]["price_sum"] += price_value
        area_buckets[bucket]["area_sum"] += area_value

    result = []

    for bucket_name, stats in area_buckets.items():
        count = stats["count"]
        avg_price = stats["price_sum"] / count if count else 0
        avg_area = stats["area_sum"] / count if count else 0
        price_per_m2 = avg_price / avg_area if avg_area > 0 else 0

        result.append({
            "rango_area": bucket_name,
            "cantidad_propiedades": count,
            "precio_promedio": round(avg_price, 2),
            "area_promedio": round(avg_area, 2),
            "precio_promedio_por_m2": round(price_per_m2, 2),
        })

    return {
        "comparacion_precio_area": result,
    }


def get_price_vs_bedrooms_stats():
    data = get_all_data()

    bedroom_stats = defaultdict(lambda: {"count": 0, "price_sum": 0.0})

    for doc in data:
        bedrooms = doc.get("habitaciones")
        price = doc.get("precio")

        if not isinstance(bedrooms, (int, float)) or not isinstance(price, (int, float)):
            continue

        key = int(bedrooms)
        stats = bedroom_stats[key]
        stats["count"] += 1
        stats["price_sum"] += float(price)

    result = []

    for bedrooms, stats in sorted(bedroom_stats.items(), key=lambda item: item[0]):
        count = stats["count"]
        avg_price = stats["price_sum"] / count if count else 0

        result.append({
            "habitaciones": bedrooms,
            "cantidad_propiedades": count,
            "precio_promedio": round(avg_price, 2),
            "total_precio": round(stats["price_sum"], 2),
        })

    return {
        "comparacion_precio_habitaciones": result,
    }


def get_correlation_matrix_data():
    data = get_all_data()

    result = []

    for doc in data:
        price = doc.get("precio")
        bedrooms = doc.get("habitaciones")
        bathrooms = doc.get("banos")
        area = doc.get("area_construida")

        if not isinstance(price, (int, float)):
            continue

        if not isinstance(bedrooms, (int, float)):
            continue

        if not isinstance(bathrooms, (int, float)):
            continue

        if not isinstance(area, (int, float)):
            continue

        result.append({
            "precio": float(price),
            "habitaciones": int(bedrooms),
            "banos": int(bathrooms),
            "area_construida": float(area),
        })

    return {
        "total_registros": len(result),
        "columnas": ["precio", "habitaciones", "banos", "area_construida"],
        "datos": result,
    }


def get_market_insights():
    data = get_all_data()

    city_data = defaultdict(lambda: {
        "prices": [],
        "price_per_m2": [],
        "year_prices": defaultdict(list),
        "count": 0,
    })

    for doc in data:
        city = doc.get("ubicacion", {}).get("ciudad")
        price = doc.get("precio")
        area = doc.get("area_construida")
        year = doc.get("tiempo", {}).get("anio")

        if not city or not isinstance(price, (int, float)):
            continue

        city_key = str(city).strip().lower()
        stats = city_data[city_key]
        price_value = float(price)

        stats["count"] += 1
        stats["prices"].append(price_value)

        if isinstance(area, (int, float)) and float(area) > 0:
            stats["price_per_m2"].append(price_value / float(area))

        if isinstance(year, int):
            stats["year_prices"][year].append(price_value)

    if not city_data:
        return {
            "total_ciudades_analizadas": 0,
            "insights": {
                "zona_crecimiento_fuerte": None,
                "propiedades_subvaloradas": [],
                "volatilidad_precios": None,
                "mercado_emergente": None,
                "recomendaciones_inversion": [],
                "tendencias_generales": [],
            },
            "detalle_por_ciudad": [],
        }

    global_price_per_m2_values = []
    city_metrics = []

    for city, stats in city_data.items():
        avg_price = sum(stats["prices"]) / len(stats["prices"]) if stats["prices"] else 0

        if len(stats["prices"]) > 1 and avg_price > 0:
            volatility = statistics.pstdev(stats["prices"]) / avg_price
        else:
            volatility = 0

        avg_price_per_m2 = (
            sum(stats["price_per_m2"]) / len(stats["price_per_m2"])
            if stats["price_per_m2"]
            else 0
        )

        if avg_price_per_m2 > 0:
            global_price_per_m2_values.append(avg_price_per_m2)

        years = sorted(stats["year_prices"].keys())
        first_year = years[0] if years else None
        last_year = years[-1] if years else None

        first_year_avg = (
            sum(stats["year_prices"][first_year]) / len(stats["year_prices"][first_year])
            if first_year is not None and stats["year_prices"][first_year]
            else None
        )
        last_year_avg = (
            sum(stats["year_prices"][last_year]) / len(stats["year_prices"][last_year])
            if last_year is not None and stats["year_prices"][last_year]
            else None
        )

        if first_year_avg and first_year_avg > 0 and last_year_avg is not None:
            growth_pct = ((last_year_avg - first_year_avg) / first_year_avg) * 100
        else:
            growth_pct = 0

        city_metrics.append({
            "ciudad": city,
            "cantidad_propiedades": stats["count"],
            "precio_promedio": round(avg_price, 2),
            "precio_promedio_por_m2": round(avg_price_per_m2, 2),
            "volatilidad": round(volatility, 4),
            "crecimiento_porcentual": round(growth_pct, 2),
            "primer_anio": first_year,
            "ultimo_anio": last_year,
        })

    global_avg_price_per_m2 = (
        sum(global_price_per_m2_values) / len(global_price_per_m2_values)
        if global_price_per_m2_values
        else 0
    )

    strongest_growth_city = max(city_metrics, key=lambda item: item["crecimiento_porcentual"])
    highest_volatility_city = max(city_metrics, key=lambda item: item["volatilidad"])

    undervalued_candidates = [
        city for city in city_metrics
        if city["precio_promedio_por_m2"] > 0 and city["precio_promedio_por_m2"] < global_avg_price_per_m2
    ]
    undervalued_candidates.sort(key=lambda item: item["precio_promedio_por_m2"])

    emerging_candidates = [
        city for city in city_metrics
        if city["crecimiento_porcentual"] > 0
        and city["precio_promedio_por_m2"] > 0
        and city["precio_promedio_por_m2"] <= global_avg_price_per_m2
        and city["cantidad_propiedades"] >= 5
    ]
    emerging_candidates.sort(
        key=lambda item: (item["crecimiento_porcentual"], -item["precio_promedio_por_m2"]),
        reverse=True,
    )

    bullish_count = len([city for city in city_metrics if city["crecimiento_porcentual"] > 0])
    bearish_count = len([city for city in city_metrics if city["crecimiento_porcentual"] < 0])

    trend_summary = []
    trend_summary.append(
        f"{bullish_count} ciudades muestran crecimiento de precio promedio y {bearish_count} muestran caida."
    )
    trend_summary.append(
        f"El precio promedio por m2 global estimado es {round(global_avg_price_per_m2, 2)}."
    )

    recommendations = []
    recommendations.append(
        f"Seguir de cerca {strongest_growth_city['ciudad']} por su crecimiento de {strongest_growth_city['crecimiento_porcentual']}%."
    )

    if undervalued_candidates:
        recommendations.append(
            f"Evaluar oportunidades de valor en {undervalued_candidates[0]['ciudad']} por su menor precio por m2 frente al promedio global."
        )

    recommendations.append(
        f"Gestionar riesgo en {highest_volatility_city['ciudad']} por mayor volatilidad relativa ({highest_volatility_city['volatilidad']})."
    )

    return {
        "total_ciudades_analizadas": len(city_metrics),
        "insights": {
            "zona_crecimiento_fuerte": strongest_growth_city,
            "propiedades_subvaloradas": undervalued_candidates[:3],
            "volatilidad_precios": highest_volatility_city,
            "mercado_emergente": emerging_candidates[0] if emerging_candidates else None,
            "recomendaciones_inversion": recommendations,
            "tendencias_generales": trend_summary,
        },
        "detalle_por_ciudad": sorted(
            city_metrics,
            key=lambda item: item["crecimiento_porcentual"],
            reverse=True,
        ),
    }


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

    counts = Counter()

    for doc in data:
        tipo = doc.get("propiedad", {}).get("tipo_propiedad", "")
        counts[classify_property_type(tipo)] += 1

    return {
        "total_processed": len(data),
        "message": "Conteo por tipo de propiedad completado",
        "counts": dict(sorted(counts.items()))
    }

def analyze_data_quality():
    data = get_all_data()

    result = analyze_quality(data)

    return result


def get_properties_page_data(page=1, page_size=15, filters=None):
    items = get_properties_page(page_size=page_size, page=page, filters=filters)
    total = count_properties(filters)
    has_more = (page * page_size) < total

    return {
        "items": items,
        "page": page,
        "pageSize": page_size,
        "count": len(items),
        "total": total,
        "next_page": page + 1 if has_more else None,
        "has_more": has_more,
    }