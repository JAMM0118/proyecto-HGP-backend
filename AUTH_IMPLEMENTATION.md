# 🔐 Implementación Mejorada del módulo Auth

## ✅ Cambios Implementados

### 1. **Autenticación JWT**
- ✨ Generación de tokens JWT al hacer login
- 🔒 Protección de endpoints con decorador `@token_required`
- ⏱️ Tokens con expiración configurable (24 horas por defecto)
- 📝 Payload incluye: user_id, email, iat, exp

**Archivo:** `app/modules/auth/jwt_utils.py`

```python
# Uso en routes protegidas
@auth_bp.route("/profile", methods=["GET"])
@token_required
def profile(token_payload):
    # token_payload contiene: {'user_id': '...', 'email': '...', 'iat': ..., 'exp': ...}
    pass
```

### 2. **Validación de Email**
- ✅ Validación de formato de email con regex
- 📧 Previene emails inválidos en registro

**Validaciones:**
- Debe contener @
- Debe tener dominio válido
- Formato: `user@domain.com`

### 3. **Validación de Contraseña Fuerte**
- 🔐 Mínimo 8 caracteres
- 🔤 Al menos una mayúscula
- 🔡 Al menos una minúscula
- 🔢 Al menos un número
- ✨ Al menos un carácter especial

**Caracteres especiales permitidos:** `!@#$%^&*(),.?":{}|<>`

### 4. **Rate Limiting**
- 🚫 Máximo 5 registros por hora por IP
- 🚫 Máximo 10 logins por hora por IP
- ⏱️ Protección contra ataques de fuerza bruta

**Archivo:** `app/extensions/limiter.py`

### 5. **Campos de Auditoría**
- 📅 `created_at` - Fecha de creación del usuario
- 📅 `updated_at` - Fecha de última actualización
- ✅ `is_active` - Estado del usuario
- 🔑 `last_login` - Último acceso exitoso

### 6. **Variables de Entorno**
- 🔑 `JWT_SECRET_KEY` - Clave secreta para JWT
- 🔐 `JWT_ALGORITHM` - Algoritmo (HS256)
- ⏰ `JWT_EXPIRATION_HOURS` - Expiración de tokens
- 🗄️ `MONGO_URI` - Conexión a MongoDB

**Archivo:** `.env.example`

---

## 📋 Nuevos Endpoints

### 1. POST `/api/auth/register`
Registra un nuevo usuario

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe"
}
```

**Response (201):**
```json
{
  "message": "Usuario registrado correctamente",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe"
  }
}
```

**Errores:**
- 400: Email/contraseña/nombre requeridos
- 400: Email inválido
- 400: Contraseña débil
- 409: Email ya existe
- 429: Rate limit excedido

---

### 2. POST `/api/auth/login`
Autentica usuario y retorna JWT

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Inicio de sesión exitoso",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

**Errores:**
- 400: Email/contraseña requeridos
- 401: Credenciales inválidas
- 403: Usuario desactivado
- 429: Rate limit excedido

---

### 3. GET `/api/auth/profile`
Obtiene el perfil del usuario autenticado

**Headers requeridos:**
```
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe",
    "created_at": "2026-05-28T21:26:43.699Z",
    "last_login": "2026-05-28T21:34:52.123Z"
  }
}
```

**Errores:**
- 401: Token requerido
- 401: Token inválido o expirado
- 404: Usuario no encontrado

---

## 🗄️ Schema de Usuarios (MongoDB)

```javascript
{
  "_id": ObjectId,
  "email": String,           // único, minúsculas
  "password": String,        // hasheada
  "name": String,
  "is_active": Boolean,      // por defecto true
  "created_at": Date,
  "updated_at": Date,
  "last_login": Date         // null si nunca ha entrado
}
```

---

## 🛠️ Instalación y Uso

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar variables de entorno
```bash
# Copiar .env.example a .env
cp .env.example .env

# Editar .env con tus valores
JWT_SECRET_KEY=your-super-secret-key-change-this
MONGO_URI=mongodb://localhost:27017/mydb
```

### 3. Iniciar servidor
```bash
python run.py
```

### 4. Probar endpoints (necesita MongoDB activo)
```bash
python test_auth_v2.py
```

---

## 📦 Dependencias Nuevas

```
PyJWT==2.13.0              # Autenticación JWT
Flask-Limiter==3.5.0       # Rate limiting
python-dotenv==1.0.0       # Variables de entorno
```

---

## 🔄 Flujo de Autenticación

```
1. Usuario se registra (POST /register)
   ↓
2. Validación de email, contraseña y nombre
   ↓
3. Se hashea la contraseña
   ↓
4. Se crea usuario en MongoDB
   ↓
5. Usuario hace login (POST /login)
   ↓
6. Se validan credenciales
   ↓
7. Se genera JWT con user_id y email
   ↓
8. JWT se retorna al cliente
   ↓
9. Cliente incluye JWT en header: Authorization: Bearer {token}
   ↓
10. Servidor verifica JWT en @token_required
   ↓
11. Usuario accede a ruta protegida (GET /profile)
```

---

## 🔐 Seguridad

✅ **Implementado:**
- Contraseñas hasheadas con werkzeug.security
- JWT firmados con algoritmo HS256
- Rate limiting para prevenir fuerza bruta
- Validación de email y contraseña
- Tokens con expiración

⚠️ **Para Producción:**
- Cambiar JWT_SECRET_KEY a valor único y seguro
- Usar HTTPS siempre
- Configurar CORS apropiadamente
- Implementar HTTPS_ONLY en cookies
- Usar environment variables secretas

---

## 📝 Archivos Modificados

```
app/
├── __init__.py                          # Cargar dotenv, limiter, JWT config
├── extensions/
│   ├── limiter.py                       # NUEVO: Flask-Limiter config
├── modules/auth/
│   ├── model.py                         # ACTUALIZADO: Audit fields
│   ├── routes.py                        # ACTUALIZADO: JWT, rate limiting
│   ├── service.py                       # ACTUALIZADO: Validaciones, JWT
│   ├── validators.py                    # NUEVO: Email y password validators
│   └── jwt_utils.py                     # NUEVO: Funciones JWT

requirements.txt                         # NUEVO: Dependencies
.env.example                             # NUEVO: Template de variables
```

---

## 🧪 Tests Incluidos

`test_auth_v2.py` - Script que valida:
- ✅ Registro exitoso
- ✅ Rechazo de contraseña débil
- ✅ Rechazo de email inválido
- ✅ Rechazo de duplicado
- ✅ Login exitoso con JWT
- ✅ Acceso a perfil con token
- ✅ Rechazo de login fallido
- ✅ Rechazo sin token

---

## 💡 Próximas Mejoras (Opcionales)

- [ ] Confirmación de email
- [ ] Recuperación de contraseña
- [ ] Refresh tokens
- [ ] Roles y permisos
- [ ] 2FA (Two-Factor Authentication)
- [ ] Integración con OAuth (Google, GitHub)
- [ ] Blacklist de tokens revocados

---

## 📧 Soporte

Si hay problemas con MongoDB, asegúrate que esté corriendo:
```bash
# Windows
mongod

# Linux/Mac
brew services start mongodb-community
```

---

**Implementado con:** Flask, PyJWT, Flask-Limiter, MongoDB ✨
