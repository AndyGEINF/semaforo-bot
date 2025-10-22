# 🚀 Guía Rápida: Deploy en Render

## 📋 Requisitos Previos
- ✅ Cuenta en GitHub
- ✅ Repositorio público: `AndyGEINF/semaforo-bot`
- ✅ Archivo `render.yaml` en el repo (ya lo tienes)

---

## 🎯 Paso a Paso

### **PASO 1: Crear Cuenta en Render**

1. Ve a **https://render.com**
2. Click en **"Get Started"** (botón azul grande)
3. Selecciona **"Sign Up with GitHub"**
4. Autoriza a Render

---

### **PASO 2: Nuevo Blueprint**

1. En el Dashboard de Render, busca el botón **"New +"** (esquina superior derecha)
2. En el menú desplegable, selecciona **"Blueprint"**
3. Verás una pantalla "Connect a repository"

---

### **PASO 3: Conectar Repositorio**

**Opción A: Si ya autorizaste GitHub**
- Busca en la lista: `AndyGEINF/semaforo-bot`
- Click en **"Connect"**

**Opción B: Si no aparece el repo**
- Click en **"Configure GitHub App"**
- Selecciona **"All repositories"** o solo `semaforo-bot`
- Click **"Save"**
- Regresa a Render y busca el repo

---

### **PASO 4: Configurar Blueprint**

Render detectará automáticamente el archivo `render.yaml`. Verás:

```
✅ render.yaml found
```

**Configuración:**
- **Blueprint Name:** `semaforo-bot` (o el que prefieras)
- **Branch:** `main` (ya seleccionado)
- **Environment:** Production

**Click en el botón azul: "Apply"**

---

### **PASO 5: Deploy Automático** ⏳

Render comenzará a crear 4 servicios:

1. **semaforo-bot-main** (Web Service)
   - Puerto: 8000
   - Tipo: Python
   - Estado: 🟡 Building...

2. **semaforo-bot-longshort** (Web Service)
   - Puerto: 8001
   - Tipo: Python
   - Estado: 🟡 Building...

3. **semaforo-bot-frontend** (Static Site)
   - Puerto: 443 (HTTPS)
   - Estado: 🟡 Building...

4. **semaforo-redis** (Redis Database)
   - Plan: Free
   - Estado: 🟡 Creating...

**Tiempo estimado:** 10-15 minutos

---

### **PASO 6: Monitorear Deploy**

Verás logs en tiempo real:

```bash
==> Installing dependencies
==> pip install -r requirements.txt
==> playwright install chromium --with-deps  # ← Esto tarda ~8 min
==> Build successful
==> Starting service
==> Service is live ✅
```

**Estados posibles:**
- 🟡 **Building** - Instalando dependencias
- 🟢 **Live** - Funcionando correctamente
- 🔴 **Failed** - Error (revisa logs)
- ⚪ **Sleeping** - Dormido (plan gratuito)

---

### **PASO 7: Obtener URLs**

Una vez completado, verás 3 URLs públicas:

```
🌐 Frontend
https://semaforo-bot-frontend.onrender.com

🔌 API Principal
https://semaforo-bot-main.onrender.com

📊 API Long/Short
https://semaforo-bot-longshort.onrender.com
```

---

## ✅ Verificar que Funciona

### **1. Probar Frontend**
```
https://semaforo-bot-frontend.onrender.com
```
Deberías ver el dashboard de SemáforoBot

### **2. Probar API Principal**
```
https://semaforo-bot-main.onrender.com/docs
```
Deberías ver la documentación de FastAPI (Swagger UI)

### **3. Probar Health Check**
```
https://semaforo-bot-main.onrender.com/status
```
Respuesta esperada:
```json
{
  "status": "ok",
  "timestamp": "2025-10-22T..."
}
```

---

## ⚙️ Configuración Adicional (Opcional)

### **Variables de Entorno**

Si necesitas añadir API keys u otras variables:

1. Click en el servicio (ej: `semaforo-bot-main`)
2. Ve a **"Environment"** en el menú lateral
3. Click **"Add Environment Variable"**
4. Añade:
   ```
   EXCHANGE_API_KEY=tu_clave_aquí
   EXCHANGE_API_SECRET=tu_secreto_aquí
   ```
5. Click **"Save Changes"**
6. El servicio se reiniciará automáticamente

---

## 🔧 Troubleshooting

### **Error: "Build Failed"**

**Solución:**
1. Ve a la pestaña **"Logs"**
2. Busca el error (línea en rojo)
3. Errores comunes:
   - Falta dependencia en `requirements.txt`
   - Error de sintaxis en Python
   - Playwright no se instaló

**Fix rápido:**
```bash
# En tu repo local
git add .
git commit -m "fix: corregir error de build"
git push
# Render redeployará automáticamente
```

---

### **Error: "Service Unavailable"**

**Causa:** El servicio está durmiendo (plan gratuito)

**Solución:**
- Espera 30-60 segundos
- Refresca la página
- El servicio despertará automáticamente

---

### **Error: Playwright no funciona**

**Síntomas:**
- Logs muestran: "Playwright browser not found"

**Solución:**
Verifica que `render.yaml` tenga:
```yaml
buildCommand: "pip install -r requirements.txt && playwright install chromium --with-deps"
```

---

## 🔄 Actualizaciones Automáticas

Cada vez que hagas `git push` a la rama `main`:
1. Render detecta el cambio
2. Hace deploy automático
3. Los servicios se actualizan (sin downtime)

---

## 💰 Plan Gratuito - Limitaciones

| Recurso | Límite |
|---------|--------|
| **Horas/mes** | 750 horas gratis |
| **RAM** | 512 MB |
| **CPU** | Compartida |
| **Inactividad** | Se duerme tras 15 min |
| **Wake-up** | ~30-60 segundos |
| **Build time** | Sin límite |
| **Bandwidth** | 100 GB/mes |

**Tip:** Usa un cron job externo (cron-job.org) para hacer ping cada 10 minutos y mantener el servicio despierto.

---

## 📞 Soporte

- **Documentación Render:** https://render.com/docs
- **Community Forum:** https://community.render.com
- **Status Page:** https://status.render.com

---

## 🎉 ¡Listo!

Tu SemáforoBot ahora está desplegado en Render con:
- ✅ HTTPS automático
- ✅ Deploy continuo desde GitHub
- ✅ Redis incluido
- ✅ Logs en tiempo real
- ✅ Métricas de rendimiento

**URL pública:** https://semaforo-bot-frontend.onrender.com

---

**Última actualización:** 2025-10-22  
**Versión:** 1.0.0
