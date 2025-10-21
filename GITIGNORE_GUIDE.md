# 📋 Guía del .gitignore

## ¿Qué hace este archivo?

El `.gitignore` le dice a Git qué archivos **NO subir** a GitHub. Esto es importante para:
- 🔒 **Proteger secretos** (API keys, contraseñas)
- 🚀 **Mantener el repo limpio** (sin archivos temporales)
- 💾 **Reducir tamaño** (sin node_modules, venv, etc.)

---

## 📦 Archivos Excluidos

### 🔒 **Secretos y Configuración Sensible**
```
.env                    # ❌ Nunca subir (contiene API keys)
.env.local
config.local.json
secrets.json
```
✅ **Mantener:** `.env.example` (plantilla sin secretos)

### 🐍 **Python**
```
__pycache__/            # Cache de Python
*.pyc                   # Archivos compilados
venv/                   # Entorno virtual (≈200MB)
.pytest_cache/          # Cache de tests
```

### 🌐 **Playwright y Navegadores**
```
.playwright/            # Navegadores instalados (≈500MB)
playwright-report/
test-results/
screenshots/
```

### 💾 **Base de Datos**
```
*.db                    # Bases de datos SQLite
*.sqlite
redis_data/             # Datos de Redis
dump.rdb
```

### 🛠️ **IDEs y Editores**
```
.vscode/                # Configuración de VSCode
.idea/                  # PyCharm
*.swp                   # Vim
```

### 📊 **Logs y Temporales**
```
*.log                   # Archivos de log
logs/
*.tmp
*.bak
backups/
```

### 🖥️ **Sistema Operativo**
```
.DS_Store              # macOS
Thumbs.db              # Windows
desktop.ini
```

---

## ✅ Archivos Incluidos (NO ignorados)

Estos archivos **SÍ se suben** a GitHub:

```
✅ main.py                              # Código fuente
✅ api_longshort_ondemand.py
✅ scrape_coinglass_v6_dropdown.py
✅ requirements.txt                     # Dependencias
✅ config.json                          # Configuración general
✅ .env.example                         # Plantilla de variables
✅ README.md                            # Documentación
✅ DEPLOYMENT.md                        # Guía de despliegue
✅ render.yaml                          # Config de Render
✅ Procfile                             # Config de Railway
✅ .gitignore                           # Este archivo
✅ static/index_pro.html                # Frontend
✅ data_adapter/                        # Módulos Python
✅ strategy/
✅ semaforo-bot/
```

---

## 🔍 Verificar Qué Se Subirá

Antes de hacer commit, verifica qué archivos se incluirán:

```bash
# Ver archivos que Git va a trackear
git add .
git status

# Deberías ver algo como:
# ✅ new file:   main.py
# ✅ new file:   requirements.txt
# ✅ new file:   README.md
# ❌ NO deberías ver: .env, venv/, __pycache__/
```

---

## ⚠️ Si Subiste un Archivo por Error

Si subiste `.env` o algún secreto por error:

```bash
# 1. Removerlo del repo (pero mantenerlo local)
git rm --cached .env

# 2. Hacer commit
git commit -m "Remove .env from repository"

# 3. Push
git push

# 4. Cambiar TODAS las API keys que estaban en ese archivo
#    (¡ya están expuestas!)
```

---

## 🧪 Probar el .gitignore

```bash
# Ver qué archivos serían ignorados
git status --ignored

# Verificar un archivo específico
git check-ignore -v .env
# Debería mostrar: .gitignore:XX:.env     .env
```

---

## 📝 Personalizar

Si necesitas ignorar archivos específicos de tu proyecto:

```gitignore
# Añadir al final de .gitignore:

# Mis archivos personales
mi_script_local.py
datos_privados/
```

---

## 🔄 Actualizar .gitignore Después de Commits

Si añades reglas nuevas al `.gitignore` después de haber hecho commits:

```bash
# Limpiar cache de Git
git rm -r --cached .

# Re-añadir todo (ahora respetando el nuevo .gitignore)
git add .

# Commit
git commit -m "Update .gitignore"
```

---

## ✨ Buenas Prácticas

1. ✅ **Siempre** usa `.env.example` como plantilla
2. ✅ **Nunca** subas API keys, passwords, tokens
3. ✅ **Ignora** node_modules, venv, __pycache__
4. ✅ **Revisa** con `git status` antes de commit
5. ✅ **Documenta** en README qué variables necesita el `.env`

---

## 🆘 Si Tienes Dudas

- ¿Este archivo debería estar en Git? → Pregúntate: "¿Contiene secretos? ¿Es generado automáticamente?"
- Si SÍ a cualquiera → ❌ No subir (añadir a .gitignore)
- Si NO a ambas → ✅ Subir

---

**Última actualización:** 2025-10-20  
**Versión:** 1.0.0
