# 🚀 Guía de Despliegue - SemáforoBot

## 📋 Resumen del Proyecto

**SemáforoBot** es una aplicación de análisis de trading que requiere:
- ✅ Backend Python (FastAPI) - 2 servidores
- ✅ Frontend estático (HTML/JS)
- ✅ Redis (base de datos en memoria)
- ✅ Playwright (navegador headless para scraping)
- ✅ Websockets/SSE (Server-Sent Events)

---

## 🔍 Análisis de Plataformas de Despliegue

### 1. **Vercel** ❌ **NO RECOMENDADO**

**Por qué NO funciona:**
- ❌ Orientado a Next.js/Node.js, no Python
- ❌ Serverless functions con límite de 10 segundos (necesitamos procesos largos)
- ❌ No soporta WebSockets/SSE de larga duración
- ❌ No permite Playwright (navegador headless)
- ❌ Sin Redis nativo

**Veredicto:** ❌ **Incompatible con este proyecto**

---

### 2. **Firebase** ❌ **NO RECOMENDADO**

**Por qué NO funciona:**
- ❌ Cloud Functions: límite de tiempo (9 min máximo)
- ❌ No soporta Python de forma nativa (solo Node.js, Python limitado)
- ❌ Sin Redis nativo (necesitarías Firestore/Realtime DB)
- ❌ Playwright no funciona en Cloud Functions
- ❌ SSE/WebSockets complicados de implementar

**Veredicto:** ❌ **Incompatible con este proyecto**

---

### 3. **Render** ✅ **RECOMENDADO** (Plan Gratuito)

**Por qué SÍ funciona:**
- ✅ Soporta Python nativo
- ✅ Web Services con procesos de larga duración
- ✅ WebSockets y SSE funcionan perfectamente
- ✅ Redis nativo (plan gratuito disponible)
- ✅ Playwright funciona (con configuración adicional)
- ✅ Variables de entorno
- ✅ Deploy automático desde GitHub
- ✅ SSL/HTTPS gratuito

**Limitaciones del plan gratuito:**
- ⚠️ Se duerme después de 15 min de inactividad (tarda ~1 min en despertar)
- ⚠️ 750 horas/mes gratis
- ⚠️ 512 MB RAM
- ⚠️ Shared CPU

**Veredicto:** ✅ **MEJOR OPCIÓN GRATUITA**

---

### 4. **Railway** ✅ **ALTERNATIVA RECOMENDADA**

**Por qué SÍ funciona:**
- ✅ Soporta Python, Redis, PostgreSQL
- ✅ Procesos de larga duración
- ✅ WebSockets/SSE soportados
- ✅ Playwright funciona
- ✅ Mejor rendimiento que Render
- ✅ Deploy desde GitHub

**Limitaciones del plan gratuito:**
- ⚠️ $5 de crédito mensual (suficiente para uso ligero)
- ⚠️ Requiere tarjeta de crédito (no cobran si no pasas del crédito)

**Veredicto:** ✅ **MEJOR RENDIMIENTO** (requiere tarjeta)

---

### 5. **Fly.io** ✅ **ALTERNATIVA TÉCNICA**

**Por qué SÍ funciona:**
- ✅ Python nativo
- ✅ Redis soportado
- ✅ Playwright funciona
- ✅ No se duerme (always-on)
- ✅ Mejor rendimiento

**Limitaciones del plan gratuito:**
- ⚠️ Requiere tarjeta de crédito
- ⚠️ 3 GB de transferencia/mes
- ⚠️ Configuración más técnica (Dockerfile)

**Veredicto:** ✅ **Opción avanzada**

---

### 6. **Koyeb** ✅ **OPCIÓN SIMPLE**

**Por qué SÍ funciona:**
- ✅ Python nativo
- ✅ Deploy fácil desde GitHub
- ✅ WebSockets/SSE
- ✅ No se duerme
- ✅ SSL gratuito

**Limitaciones del plan gratuito:**
- ⚠️ 512 MB RAM
- ⚠️ 2.5 GB disco
- ⚠️ Redis externo necesario (Upstash gratuito)

**Veredicto:** ✅ **Buena opción simple**

---

## 🏆 Recomendación Final

### **Para empezar (100% GRATIS, sin tarjeta):**
```
Frontend → Vercel/Netlify (estáticos)
Backend  → Render (Web Service)
Redis    → Render (Redis Instance) o Upstash (gratuito)
```

### **Para mejor rendimiento (requiere tarjeta, pero gratis):**
```
Todo en Railway o Fly.io
```

---

## 📦 Opción 1: Despliegue en Render (RECOMENDADO)

### **Paso 1: Preparar el proyecto**

1. **Crear `render.yaml` en la raíz:**

```yaml
services:
  # Servidor principal (main.py)
  - type: web
    name: semaforo-bot-main
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt && playwright install chromium --with-deps"
    startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
    envVars:
      - key: REDIS_URL
        fromDatabase:
          name: semaforo-redis
          property: connectionString
      - key: PYTHON_VERSION
        value: 3.11.0
      - key: EXCHANGE_NAME
        value: binance
    healthCheckPath: /status

  # Servidor SSE Long/Short (api_longshort_ondemand.py)
  - type: web
    name: semaforo-bot-longshort
    env: python
    region: oregon
    plan: free
    buildCommand: "pip install -r requirements.txt && playwright install chromium --with-deps"
    startCommand: "python api_longshort_ondemand.py"
    envVars:
      - key: PYTHON_VERSION
        value: 3.11.0
    healthCheckPath: /status

  # Frontend estático
  - type: web
    name: semaforo-bot-frontend
    env: static
    buildCommand: ""
    staticPublishPath: ./static
    routes:
      - type: rewrite
        source: /*
        destination: /index_pro.html

databases:
  # Redis para memoria
  - name: semaforo-redis
    plan: free
    region: oregon
```

2. **Actualizar `requirements.txt`:**

```txt
# Dependencias optimizadas para Render
ccxt>=4.4.0
pandas>=2.1.0
numpy>=1.26.0
ta>=0.11.0
fastapi>=0.109.0
uvicorn[standard]>=0.27.0
pydantic>=2.5.0
python-dotenv>=1.0.0
redis>=5.0.0
requests>=2.31.0
aiohttp>=3.9.0
playwright>=1.40.0
beautifulsoup4>=4.12.0
lxml>=4.9.0
python-dateutil>=2.8.0
pytz>=2023.3

# Optimizaciones para Render
gunicorn>=21.2.0
```

3. **Modificar `main.py` para usar variables de entorno de Render:**

```python
import os

# Configuración de Redis
redis_host = os.getenv('REDIS_HOST', 'localhost')
redis_port = int(os.getenv('REDIS_PORT', 6379))

# Si hay REDIS_URL (Render), parsearla
redis_url = os.getenv('REDIS_URL')
if redis_url:
    # Formato: redis://user:pass@host:port/db
    import urllib.parse
    parsed = urllib.parse.urlparse(redis_url)
    redis_host = parsed.hostname
    redis_port = parsed.port
    redis_password = parsed.password
```

4. **Crear archivo `.env.example` para documentar variables:**

```env
# Exchange
EXCHANGE_NAME=binance
EXCHANGE_API_KEY=optional
EXCHANGE_API_SECRET=optional

# Redis (Render lo provee automáticamente)
REDIS_URL=redis://localhost:6379

# Configuración
DEBUG=False
PORT=10000
```

### **Paso 2: Deploy en Render**

1. **Crear cuenta en Render:** https://render.com (gratis, sin tarjeta)
2. **Conectar GitHub:** Autorizar acceso a tu repositorio
3. **Crear Blueprint:** 
   - New → Blueprint
   - Seleccionar repositorio
   - Render detectará `render.yaml` automáticamente
4. **Deploy:** 
   - Hacer clic en "Apply"
   - Esperar 5-10 minutos (instalación de Playwright)

### **URLs resultantes:**
```
Frontend:  https://semaforo-bot-frontend.onrender.com
API Main:  https://semaforo-bot-main.onrender.com
API SSE:   https://semaforo-bot-longshort.onrender.com
```

### **Paso 3: Configurar Frontend**

Actualizar URLs en `static/index_pro.html`:

```javascript
// Cambiar de localhost a URLs de Render
const API_BASE = 'https://semaforo-bot-main.onrender.com';
const SSE_BASE = 'https://semaforo-bot-longshort.onrender.com';

// Ejemplo:
const eventSource = new EventSource(
  `${SSE_BASE}/longshort/stream/${currentSymbol}`
);
```

---

## 📦 Opción 2: Despliegue en Railway

### **Paso 1: Crear `railway.json`**

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "numReplicas": 1,
    "sleepApplication": false,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **Paso 2: Crear `Procfile`**

```procfile
web: uvicorn main:app --host 0.0.0.0 --port $PORT
longshort: python api_longshort_ondemand.py
```

### **Paso 3: Deploy**

1. Ir a https://railway.app
2. New Project → Deploy from GitHub
3. Seleccionar repositorio
4. Añadir servicio Redis (Add Database → Redis)
5. Configurar variables de entorno

---

## 📦 Opción 3: Despliegue Mixto (ÓPTIMO)

### **Mejor combinación gratuita:**

```
Frontend Estático → Vercel/Netlify (GRATIS, rápido)
Backend Python   → Render (GRATIS, soporta Playwright)
Redis            → Upstash (GRATIS, sin dormir)
```

### **Configuración:**

**1. Frontend en Vercel:**
```bash
# Desde la carpeta static/
vercel --prod
```

**2. Backend en Render:**
- Usar `render.yaml` de arriba
- Solo deploy de los 2 servicios web (sin frontend)

**3. Redis en Upstash:**
- Ir a https://upstash.com (gratis)
- Crear Redis database
- Copiar URL: `redis://default:password@endpoint.upstash.io:6379`
- Añadir como variable `REDIS_URL` en Render

---

## ⚙️ Configuración de Playwright en Render

Render requiere instalación especial de Playwright:

**En `render.yaml`:**
```yaml
buildCommand: |
  pip install -r requirements.txt && 
  playwright install chromium && 
  playwright install-deps chromium
```

**Si falla, usar Dockerfile:**

```dockerfile
FROM python:3.11-slim

# Instalar dependencias del sistema para Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libwayland-client0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxkbcommon0 \
    libxrandr2 \
    xdg-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

RUN playwright install chromium --with-deps

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 🔒 Variables de Entorno Necesarias

```env
# Obligatorias
REDIS_URL=redis://...
EXCHANGE_NAME=binance

# Opcionales (si usas API keys)
EXCHANGE_API_KEY=tu_api_key
EXCHANGE_API_SECRET=tu_api_secret

# Configuración
DEBUG=False
PORT=10000
```

---

## 📊 Comparación de Costos

| Plataforma | Plan Gratuito | Limitaciones | Requiere Tarjeta |
|------------|---------------|--------------|------------------|
| **Render** | ✅ 750h/mes | Se duerme tras 15min | ❌ No |
| **Railway** | ✅ $5/mes | Crédito limitado | ✅ Sí |
| **Fly.io** | ✅ Limitado | 3GB transfer | ✅ Sí |
| **Koyeb** | ✅ 1 servicio | 512MB RAM | ❌ No |
| **Upstash** (Redis) | ✅ 10k cmds/día | Solo Redis | ❌ No |
| **Vercel** | ❌ Solo frontend | - | ❌ No |
| **Firebase** | ❌ No compatible | - | ❌ No |

---

## 🎯 Recomendación Final Personalizada

### **Si NO tienes tarjeta de crédito:**
```
✅ Frontend: Vercel (gratis, estático)
✅ Backend:  Render (gratis, 2 servicios web)
✅ Redis:    Upstash (gratis, 10k comandos/día)
```

### **Si tienes tarjeta (pero no quieres pagar):**
```
✅ Todo en Railway ($5 gratis/mes = suficiente)
✅ O todo en Fly.io (mejor rendimiento)
```

### **Para producción (con presupuesto):**
```
✅ AWS Lightsail ($5/mes)
✅ DigitalOcean App Platform ($5/mes)
✅ Railway Pro ($5/mes)
```

---

## 🚀 Inicio Rápido: Render en 10 minutos

```bash
# 1. Clonar repositorio
git clone <tu-repo>
cd bot-semaforo

# 2. Crear render.yaml (copiar el de arriba)
# 3. Hacer commit
git add render.yaml
git commit -m "Add Render config"
git push

# 4. Ir a render.com
# 5. New → Blueprint → Conectar repo
# 6. Apply
# 7. ¡Listo! Esperar 10 min
```

---

## 📝 Checklist de Despliegue

- [ ] `render.yaml` creado
- [ ] `requirements.txt` actualizado
- [ ] Variables de entorno configuradas
- [ ] URLs actualizadas en frontend
- [ ] Playwright instalado correctamente
- [ ] Redis conectado
- [ ] Health checks funcionando
- [ ] CORS configurado (si frontend está en otro dominio)
- [ ] SSL/HTTPS activo

---

## 🐛 Troubleshooting

### **Error: "Playwright browser not found"**
```bash
# En buildCommand de render.yaml:
playwright install chromium --with-deps
```

### **Error: "Redis connection refused"**
```python
# Verificar que usas REDIS_URL de entorno
redis_url = os.getenv('REDIS_URL')
```

### **Error: "Application not responding"**
```python
# Añadir health check endpoint
@app.get("/status")
async def health_check():
    return {"status": "ok"}
```

### **Error: "Service sleeping"**
- Render gratuito se duerme tras 15min
- Usar cron job externo (ej: cron-job.org) para hacer ping cada 10min

---

## 📞 Soporte

- **Render Docs:** https://render.com/docs
- **Railway Docs:** https://docs.railway.app
- **Playwright en producción:** https://playwright.dev/python/docs/docker

---

**Fecha:** 2025-10-19  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para despliegue
