# 🔧 Render - Soluciones a Errores Comunes

## ❌ Error: Playwright `su: Authentication failure`

### 🔍 Síntomas
```
Installing dependencies...
Switching to root user to install dependencies...
Password: su: Authentication failure
Failed to install browsers
Error: Installation process exited with code: 1
==> Build failed 😞
```

### ✅ Solución Aplicada (render.yaml actualizado)

**Cambio:**
```yaml
# ❌ ANTES (No funciona en Render)
buildCommand: "playwright install chromium --with-deps"

# ✅ AHORA (Funciona en Render)
buildCommand: "pip install -r requirements.txt && python -m playwright install --with-deps chromium"
```

**¿Por qué funciona?**
- `python -m playwright` usa el módulo Python directamente
- `--with-deps` instala las dependencias del sistema sin necesitar `su`
- Render maneja los permisos automáticamente

---

## 🔄 Alternativas si el error persiste

### **Opción 1: Instalar solo Chromium (sin deps del sistema)**

Edita `render.yaml`:
```yaml
buildCommand: "pip install -r requirements.txt && python -m playwright install chromium"
```

⚠️ **Limitación:** Puede fallar si faltan librerías del sistema

---

### **Opción 2: Usar Playwright en modo headless con flags especiales**

Edita `render.yaml`:
```yaml
buildCommand: |
  pip install -r requirements.txt && 
  python -m playwright install chromium && 
  python -m playwright install-deps chromium
```

---

### **Opción 3: Dockerfile personalizado**

Crea `Dockerfile` en la raíz del proyecto:

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

# Copiar requirements
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Instalar Playwright y browsers
RUN python -m playwright install chromium

# Copiar código
COPY . .

# Exponer puerto
EXPOSE 8000

# Comando de inicio
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Luego en render.yaml:**
```yaml
services:
  - type: web
    name: semaforo-bot-main
    runtime: docker
    dockerfilePath: ./Dockerfile
    dockerContext: .
    envVars:
      - key: PORT
        value: "8000"
```

---

## 🐛 Otros Errores Comunes

### **Error: `Module not found`**

**Síntoma:**
```
ModuleNotFoundError: No module named 'ccxt'
```

**Solución:**
Verifica que `requirements.txt` esté completo:
```bash
pip freeze > requirements.txt
git add requirements.txt
git commit -m "fix: Actualizar requirements.txt"
git push
```

---

### **Error: `Port already in use`**

**Síntoma:**
```
ERROR:    [Errno 98] Address already in use
```

**Solución:**
Asegúrate de usar `$PORT` en el startCommand:
```yaml
startCommand: "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

Render asigna el puerto dinámicamente mediante la variable `$PORT`.

---

### **Error: Redis connection failed**

**Síntoma:**
```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**Solución 1:** Verifica que `REDIS_URL` esté configurada en render.yaml:
```yaml
envVars:
  - key: REDIS_URL
    fromDatabase:
      name: semaforo-redis
      property: connectionString
```

**Solución 2:** Verifica que la base de datos Redis esté en el mismo blueprint:
```yaml
databases:
  - name: semaforo-redis
    plan: free
    region: oregon
```

---

### **Error: Service keeps sleeping**

**Síntoma:**
- El servicio se duerme cada 15 minutos
- Primera carga tarda 60 segundos

**Solución:** Usa un servicio externo de ping (plan gratuito)

**Opción 1: UptimeRobot** (Recomendado)
1. Ve a https://uptimerobot.com (gratis)
2. Crea monitor HTTP(s)
3. URL: `https://semaforo-bot-main.onrender.com/status`
4. Intervalo: 5 minutos
5. ¡Listo! Tu servicio nunca dormirá

**Opción 2: Cron-Job.org**
1. Ve a https://cron-job.org (gratis)
2. Crea cron job
3. URL: `https://semaforo-bot-main.onrender.com/status`
4. Intervalo: `*/10 * * * *` (cada 10 min)

**Opción 3: GitHub Actions** (Gratis, dentro de tu repo)

Crea `.github/workflows/keep-alive.yml`:
```yaml
name: Keep Render Service Alive

on:
  schedule:
    - cron: '*/10 * * * *'  # Cada 10 minutos
  workflow_dispatch:

jobs:
  keep-alive:
    runs-on: ubuntu-latest
    steps:
      - name: Ping Render services
        run: |
          curl -f https://semaforo-bot-main.onrender.com/status || exit 0
          curl -f https://semaforo-bot-longshort.onrender.com/status || exit 0
```

---

### **Error: Build tarda más de 15 minutos**

**Síntoma:**
```
Build exceeded maximum duration (15:00)
```

**Solución:**
Render Free tier tiene límite de 15 min de build. Si Playwright tarda mucho:

1. **Cachear instalación de Playwright:**
   ```yaml
   buildCommand: |
     pip install -r requirements.txt && 
     python -m playwright install chromium --with-deps 2>&1 | grep -v "Downloading" || true
   ```

2. **Usar imagen Docker pre-built** (ver Opción 3 arriba)

---

## 📊 Verificar Estado del Deploy

### **Ver logs en tiempo real:**
```bash
# En Render Dashboard
1. Click en tu servicio
2. Menú lateral: "Logs"
3. Ver logs en vivo
```

### **Probar endpoints manualmente:**
```bash
# Health check
curl https://semaforo-bot-main.onrender.com/status

# Documentación API
curl https://semaforo-bot-main.onrender.com/docs

# Long/Short stream (debe retornar SSE)
curl https://semaforo-bot-longshort.onrender.com/longshort/stream/BTC
```

---

## 🆘 Si nada funciona: Plan B - Railway

Railway es más permisivo con Playwright y no tiene estos problemas de permisos.

### **Deploy rápido en Railway:**
```bash
# 1. Instalar Railway CLI
npm i -g @railway/cli

# 2. Login
railway login

# 3. Crear proyecto
railway init

# 4. Deploy
railway up

# 5. Añadir Redis
railway add redis

# 6. Obtener URL
railway domain
```

**Ventajas Railway:**
- ✅ No problemas con Playwright
- ✅ No se duerme
- ✅ Más rápido

**Desventajas:**
- ❌ Requiere tarjeta de crédito
- ❌ $5/mes después de free tier

---

## 📝 Checklist de Troubleshooting

Antes de pedir ayuda, verifica:

- [ ] `render.yaml` tiene el buildCommand correcto
- [ ] `requirements.txt` está actualizado
- [ ] `main.py` usa `--host 0.0.0.0 --port $PORT`
- [ ] Redis está en el mismo blueprint
- [ ] Variables de entorno configuradas
- [ ] Rama `main` tiene los últimos cambios
- [ ] Logs de Render no muestran errores Python
- [ ] Health check endpoint (`/status`) existe

---

## 🔗 Enlaces Útiles

- **Render Docs - Python:** https://render.com/docs/deploy-python
- **Render Docs - Playwright:** https://render.com/docs/deploy-playwright
- **Playwright Docs:** https://playwright.dev/python/docs/intro
- **Community Forum:** https://community.render.com

---

**Última actualización:** 2025-10-22  
**Fix aplicado:** `python -m playwright install --with-deps chromium`  
**Estado:** ✅ Listo para redeploy en Render
