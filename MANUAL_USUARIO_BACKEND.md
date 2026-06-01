# Manual de Usuario - Backend HGP

## 1. Descripción general

Este backend es una API REST construida con Flask para la gestión de datos de propiedades, análisis de mercado y predicción de precios. Está preparado para:

- Registrar y autenticar usuarios con JWT.
- Subir y procesar archivos CSV con datos de propiedades.
- Consultar estadísticas del mercado inmobiliario.
- Entrenar un modelo de predicción de precios.
- Predecir el precio de una propiedad.

## 2. Requisitos

- Python 3.11+ (recomendado)
- MongoDB accesible desde la aplicación
- Dependencias listadas en `requirements.txt`

## 3. Instalación

1. Crear y activar un entorno virtual en la raíz del backend:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Instalar dependencias:

```powershell
pip install -r requirements.txt
```

## 4. Configuración

El backend usa variables de entorno para la configuración principal. No hay un ejemplo completo en `.env.example`, pero las variables clave son:

- `JWT_SECRET_KEY`: clave secreta para firmar JWT.
- `JWT_ALGORITHM`: algoritmo de firma JWT (por defecto `HS256`).
- `JWT_EXPIRATION_HOURS`: horas de validez del token (por defecto `24`).
- `MONGO_URI`: cadena de conexión a MongoDB (por defecto `mongodb://localhost:27017/mydb`).

Crear un archivo `.env` en la raíz con contenidos similares a:

```env
JWT_SECRET_KEY=mi_clave_secreta
JWT_ALGORITHM=HS256
JWT_EXPIRATION_HOURS=24
MONGO_URI=mongodb://localhost:27017/hgp_backend
```

## 5. Ejecución

Desde la raíz de `proyecto-HGP-backend`, ejecutar:

```powershell
python run.py
```

Esto inicia el servidor Flask en modo `debug` y escucha por defecto en `http://127.0.0.1:5000`.

## 6. Estructura de carpetas importante

- `run.py` - punto de entrada de la aplicación.
- `app/__init__.py` - crea la aplicación Flask y registra los blueprints.
- `app/extensions/db.py` - inicializa la conexión con MongoDB.
- `app/extensions/swagger.py` - habilita la documentación Swagger.
- `app/modules/auth/` - rutas, servicio y JWT para autenticación.
- `app/modules/csv/` - procesamiento y análisis de datos CSV.
- `app/modules/prediction/` - entrenamiento y predicción de precios.
- `app/models/` - modelo de predicción guardado (`property_price_model.pkl`).

## 7. Endpoints disponibles

### 7.1 Test

- `GET /api/test/`
  - Retorna un mensaje de prueba para validar que la API está activa.

### 7.2 Autenticación

#### Registro

- `POST /api/auth/register`

Cuerpo JSON:

```json
{
  "email": "user@example.com",
  "password": "strongpassword123",
  "name": "John Doe",
  "role": "usuario"
}
```

Respuesta esperada:

- `201 Created` con `message`, `user.id`, `user.email`, `user.name` y `user.role`.

#### Login

- `POST /api/auth/login`

Cuerpo JSON:

```json
{
  "email": "user@example.com",
  "password": "strongpassword123"
}
```

Respuesta esperada:

- `200 OK` con `message`, `user` y `token`.

#### Logout

- `POST /api/auth/logout`

Encabezado:

```http
Authorization: Bearer <token>
```

Respuesta esperada:

- `200 OK` con `message`.

#### Perfil

- `GET /api/auth/profile`

Encabezado:

```http
Authorization: Bearer <token>
```

Respuesta esperada:

- `200 OK` con datos del usuario autenticado.

### 7.3 CSV y análisis de datos

#### Subir CSV

- `POST /api/csv/upload`

Formulario `multipart/form-data` con el campo:

- `file`: archivo CSV a procesar.

Respuesta esperada:

- `rows`: número de filas procesadas.
- `message`: confirmación.
- `preview`: vista previa de los primeros registros.

#### Consultas de estadísticas

- `GET /api/csv/avg-price-by-city`
  - Retorna precio promedio por ciudad.

- `GET /api/csv/property-analysis-stats`
  - Retorna métricas generales de las propiedades analizadas.

- `GET /api/csv/price-distribution-stats`
  - Retorna distribución de precios por rangos.

- `GET /api/csv/market-trend-stats`
  - Retorna tendencias de mercado por año.

- `GET /api/csv/market-insights`
  - Genera insights de mercado desde los datos.

- `GET /api/csv/area-comparison-stats`
  - Compara propiedades por área construida mayor/menor a 100.

- `GET /api/csv/price-vs-area-stats`
  - Compara precio frente a área construida.

- `GET /api/csv/price-vs-bedrooms-stats`
  - Compara precio frente a número de habitaciones.

- `GET /api/csv/correlation-matrix-data`
  - Devuelve datos listos para matriz de correlación.

- `GET /api/csv/top-cities-stats`
  - Obtiene las 4 ciudades con mejores métricas.

- `GET /api/csv/top-barrio-growth-stats`
  - Obtiene los 4 barrios con mayor crecimiento porcentual.

### 7.4 Predicción de precios

#### Entrenar modelo

- `POST /api/prediction/train`

Acción:

- Entrena un modelo CatBoost con los datos disponibles en MongoDB.
- Guarda el modelo en `app/models/property_price_model.pkl`.

Respuesta esperada:

- `records`: cantidad de datos usados.
- `mae`, `mse`, `r2`: métricas del modelo.

#### Predecir precio

- `POST /api/prediction/predict`

Cuerpo JSON requerido:

```json
{
  "ciudad": "Bogotá",
  "area_construida": 120.5,
  "habitaciones": 3,
  "tipo_propiedad": "apartamento",
  "banos": 2
}
```

Respuesta esperada:

- `fecha`
- `area_construida`
- `habitaciones`
- `banos`
- `tipo_propiedad`
- `ciudad`
- `precio_estimado`

> Nota: el modelo debe estar entrenado previamente con `POST /api/prediction/train`.

## 8. Ejemplos de uso con curl

### Registrar usuario

```bash
curl -X POST http://127.0.0.1:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"strongpassword123","name":"Juan Perez","role":"usuario"}'
```

### Iniciar sesión

```bash
curl -X POST http://127.0.0.1:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"strongpassword123"}'
```

### Obtener perfil

```bash
curl -X GET http://127.0.0.1:5000/api/auth/profile \
  -H "Authorization: Bearer <token>"
```

### Subir CSV

```bash
curl -X POST http://127.0.0.1:5000/api/csv/upload \
  -F "file=@datos_propiedades.csv"
```

### Entrenar modelo de predicción

```bash
curl -X POST http://127.0.0.1:5000/api/prediction/train
```

### Predecir precio

```bash
curl -X POST http://127.0.0.1:5000/api/prediction/predict \
  -H "Content-Type: application/json" \
  -d '{"ciudad":"Bogotá","area_construida":120.5,"habitaciones":3,"tipo_propiedad":"apartamento","banos":2}'
```

## 9. Consideraciones

- La autenticación usa JWT y algunos endpoints requieren el header `Authorization: Bearer <token>`.
- El almacenamiento de datos se hace en MongoDB mediante `Flask-PyMongo`.
- La documentación Swagger está habilitada por `flasgger` si se carga la aplicación.
- El modelo de predicción se guarda localmente en `app/models/property_price_model.pkl`.
- Asegúrate de tener datos válidos y coherentes antes de entrenar y predecir.

## 10. Dependencias principales

- Flask
- Flask-PyMongo
- Flask-Limiter
- PyJWT
- python-dotenv
- flasgger
- pandas
- scikit-learn
- CatBoost

---

**Fin del manual**
