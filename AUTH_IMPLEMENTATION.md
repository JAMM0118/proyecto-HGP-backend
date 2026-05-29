# 🔐 Implementación Mejorada del módulo Auth

## ✅ Cambios Implementados

### 1. **Autenticación JWT**
- ✨ Generación de tokens JWT al hacer login
- 🔒 Protección de endpoints con decorador `@token_required`
- ⏱️ Tokens con expiración configurable (24 horas por defecto)
- 📝 Payload incluye: user_id, email, iat, exp

**Archivo:** `app/modules/auth/jwt_utils.py`

### 2. **Tipos de Usuario (Roles)**
- 👨‍💼 **Administrador** - Acceso completo
- 👤 **Invitado** - Acceso limitado (por defecto)
- 📊 **Analista de Datos** - Acceso a reportes y análisis
- ⚠️ Un usuario solo puede tener UN tipo

**Validaciones:**
- Rol requerido en registro
- Solo valores: `administrador`, `invitado`, `analista_datos`

### 3. **Logout / Invalidar Tokens**
- 🚫 Tokens invalidados al logout
- 🔐 Previene reutilización de tokens
- ⏰ Tokens guardados en blacklist con timestamp

### 4. **Validación de Email**
- ✅ Validación de formato de email con regex
- 📧 Previene emails inválidos en registro

### 5. **Validación de Contraseña Fuerte**
- 🔐 Mínimo 8 caracteres
- 🔤 Al menos una mayúscula
- 🔡 Al menos una minúscula
- 🔢 Al menos un número
- ✨ Al menos un carácter especial

### 6. **Rate Limiting**
- 🚫 Máximo 5 registros por hora por IP
- 🚫 Máximo 10 logins por hora por IP
- ⏱️ Protección contra ataques de fuerza bruta

### 7. **Campos de Auditoría**
- 📅 `created_at` - Fecha de creación del usuario
- 📅 `updated_at` - Fecha de última actualización
- ✅ `is_active` - Estado del usuario
- 🔑 `last_login` - Último acceso exitoso
- 👤 `role` - Tipo de usuario

---

## 📋 Endpoints

### 1. POST `/api/auth/register`
Registra un nuevo usuario con tipo

**Request:**
```json
{
  "email": "user@example.com",
  "password": "SecurePass123!",
  "name": "John Doe",
  "role": "analista_datos"
}
```

**Roles válidos:**
- `administrador`
- `invitado`
- `analista_datos`

**Response (201):**
```json
{
  "message": "Usuario registrado correctamente",
  "user": {
    "id": "507f1f77bcf86cd799439011",
    "email": "user@example.com",
    "name": "John Doe",
    "role": "analista_datos"
  }
}
```

**Errores:**
- 400: Email/contraseña/nombre/rol requeridos
- 400: Email inválido o contraseña débil
- 400: Rol inválido
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
    "name": "John Doe",
    "role": "analista_datos"
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

### 3. POST `/api/auth/logout`
Cierra sesión e invalida el token

**Headers requeridos:**
```
Authorization: Bearer {token}
```

**Response (200):**
```json
{
  "message": "Sesión cerrada exitosamente"
}
```

**Errores:**
- 400: Token no encontrado
- 401: Token requerido/inválido
- 500: Error del servidor

**Nota:** Después de logout, no podrás usar el mismo token.

---

### 4. GET `/api/auth/profile`
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
    "role": "analista_datos",
    "created_at": "2026-05-28T21:26:43.699Z",
    "last_login": "2026-05-28T21:34:52.123Z"
  }
}
```

**Errores:**
- 401: Token requerido/inválido
- 404: Usuario no encontrado

---

## 🗄️ Schema de Usuarios (MongoDB)

### Users Collection
```javascript
{
  "_id": ObjectId,
  "email": String,           // único, minúsculas
  "password": String,        // hasheada
  "name": String,
  "role": String,            // administrador, invitado, analista_datos
  "is_active": Boolean,      // por defecto true
  "created_at": Date,
  "updated_at": Date,
  "last_login": Date         // null si nunca ha entrado
}
```

### Token Blacklist Collection
```javascript
{
  "_id": ObjectId,
  "token": String,           // token invalidado
  "created_at": Date         // para limpieza periódica
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
JWT_SECRET_KEY=L9s8hLTO1shGkPFm9KVnqEUTFtHmMVBWC2jRVI2AXYb
MONGO_URI=mongodb://localhost:27017/mydb
JWT_EXPIRATION_HOURS=24
```

### 3. Iniciar servidor
```bash
python run.py
```

---

## 🔄 Flujo de Autenticación Completo

```
1. Usuario se registra (POST /register)
   ├─ Email válido?
   ├─ Contraseña fuerte?
   ├─ Rol válido?
   └─ Email único?
   ↓
2. Se hashea la contraseña
3. Se crea usuario en MongoDB CON TIPO
   ↓
4. Usuario hace login (POST /login)
   ├─ Email existe?
   └─ Contraseña correcta?
   ↓
5. Se genera JWT con user_id y email
6. JWT se retorna al cliente
   ↓
7. Cliente incluye JWT: Authorization: Bearer {token}
   ↓
8. Servidor verifica JWT (@token_required)
   ├─ JWT válido?
   └─ ¿Está en blacklist?
   ↓
9. Usuario accede a ruta protegida (GET /profile)
   ↓
10. Para logout (POST /logout)
    ├─ Token se agrega a blacklist
    ├─ Cliente elimina token
    └─ Futuras peticiones con ese token fallan
```

---

## 🔐 Seguridad

✅ **Implementado:**
- Contraseñas hasheadas con werkzeug.security
- JWT firmados con algoritmo HS256
- Token blacklist para logout
- Rate limiting para prevenir fuerza bruta
- Validación de email, contraseña y rol
- Tokens con expiración
- Un usuario = UN tipo solamente

⚠️ **Para Producción:**
- Cambiar JWT_SECRET_KEY a valor único y seguro
- Usar HTTPS siempre
- Configurar CORS apropiadamente
- Usar environment variables secretas
- Limpiar token_blacklist periódicamente (índice TTL)
- Implementar 2FA para administradores

---

## 📝 Archivos Modificados/Nuevos

```
app/
├── __init__.py                          # ACTUALIZADO: Cargar dotenv, limiter
├── extensions/
│   ├── limiter.py                       # NUEVO: Flask-Limiter config
├── modules/auth/
│   ├── model.py                         # ACTUALIZADO: Role + blacklist methods
│   ├── routes.py                        # ACTUALIZADO: Logout endpoint
│   ├── service.py                       # ACTUALIZADO: Role validation + logout
│   ├── validators.py                    # ACTUALIZADO: Role validation
│   └── jwt_utils.py                     # ACTUALIZADO: Check blacklist

.env                                     # NUEVO: Variables de entorno
.env.example                             # NUEVO: Template
.gitignore                               # NUEVO: Exclusiones
requirements.txt                         # ACTUALIZADO: Dependencies
AUTH_IMPLEMENTATION.md                   # NUEVO: Esta documentación
POSTMAN_GUIDE.md                         # NUEVO: Guía Postman
```

---

## 💡 Próximas Mejoras (Opcionales)

- [ ] Confirmación de email
- [ ] Recuperación de contraseña
- [ ] Refresh tokens
- [ ] Permisos específicos por rol
- [ ] 2FA (Two-Factor Authentication)
- [ ] Integración con OAuth (Google, GitHub)
- [ ] Limpieza automática de token_blacklist

---

**Implementado con:** Flask, PyJWT, Flask-Limiter, MongoDB ✨
