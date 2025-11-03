# 🔧 SOLUCIÓN DE PROBLEMAS

Esta guía te ayudará a resolver los problemas más comunes al ejecutar el bot.

---

## ⚠️ Error: ImportError

### Síntoma
```
ImportError: cannot import name 'show_dashboard' from 'handlers.notes'
```

### Causa
Importaciones circulares entre módulos.

### Solución
Este problema ya está corregido en la versión 1.0.1. Si lo ves:

1. **Verifica que tienes todos los archivos actualizados**
   ```bash
   ls handlers/
   # Deberías ver: __init__.py dashboard.py menu.py notes.py projects.py settings.py tasks.py
   ```

2. **Ejecuta el script de verificación**
   ```bash
   python verify_imports.py
   ```

3. **Si el problema persiste, descarga los archivos actualizados**

---

## 🔌 Error: No module named 'telegram'

### Síntoma
```
ModuleNotFoundError: No module named 'telegram'
```

### Causa
No has instalado las dependencias.

### Solución
```bash
# Instalar dependencias
pip install -r requirements.txt

# Si tienes problemas de permisos
pip install --user -r requirements.txt

# En macOS/Linux con pip3
pip3 install -r requirements.txt
```

---

## 🔑 Error: Unauthorized (401)

### Síntoma
```
telegram.error.Unauthorized: Unauthorized
```

### Causa
Token del bot incorrecto.

### Solución
1. **Verifica el token en config.py**
   ```python
   BOT_TOKEN = "8222314009:AAG-nc-6_IJvVMk-LH4Q5bFVO3GLOymTA4o"
   ```

2. **Obtén un nuevo token si es necesario**
   - Abre Telegram
   - Busca @BotFather
   - Envía `/mybots`
   - Selecciona tu bot
   - Presiona "API Token"

---

## 🚫 El bot no responde

### Síntoma
El bot no reacciona a mensajes ni botones.

### Posibles causas y soluciones

#### 1. El bot no está ejecutándose
```bash
# Verifica que el proceso esté corriendo
# Deberías ver "🔄 Esperando mensajes..." en la terminal

# Si no está corriendo, inícialo
python main.py
```

#### 2. Usuario no autorizado
El bot solo responde a tu ID de usuario configurado.

**Verificar:**
```python
# En config.py
AUTHORIZED_USER_ID = 6009496370  # ¿Es tu ID correcto?
```

**Obtener tu ID:**
1. Abre Telegram
2. Busca @userinfobot
3. Envía `/start`
4. Copia tu ID
5. Actualiza `config.py`

#### 3. Error en el código
```bash
# Revisa la consola donde está corriendo el bot
# Busca mensajes de error en rojo
```

---

## 💾 Error de base de datos

### Síntoma
```
sqlite3.OperationalError: no such table: projects
```

### Causa
Base de datos no inicializada correctamente.

### Solución
```bash
# 1. Detener el bot (Ctrl+C)

# 2. Eliminar base de datos corrupta
rm productivity_bot.db

# 3. Reiniciar bot (creará nueva base de datos)
python main.py

# 4. Agregar datos de prueba (opcional)
python add_sample_data.py
```

---

## ⏰ Los recordatorios no se envían

### Síntoma
El bot funciona, pero no envía el resumen diario a las 07:00.

### Posibles causas y soluciones

#### 1. El bot no está ejecutándose a esa hora
```bash
# El bot debe estar corriendo 24/7 para enviar recordatorios

# Solución en Linux/Mac: usar screen o tmux
screen -S telegram-bot
python main.py
# Presiona Ctrl+A, luego D para detach

# Volver a la sesión:
screen -r telegram-bot
```

#### 2. Zona horaria incorrecta
```python
# Verifica en config.py
DEFAULT_TIMEZONE = "Europe/Madrid"

# Cambia a tu zona horaria local
```

#### 3. Horario incorrecto
```python
# Verifica en config.py
DEFAULT_DAILY_SUMMARY_TIME = time(7, 0)  # 07:00

# Cambiar a otra hora (ejemplo 08:00):
DEFAULT_DAILY_SUMMARY_TIME = time(8, 0)
```

---

## 🐍 Error: 'async' syntax error

### Síntoma
```
SyntaxError: invalid syntax
    async def mi_funcion():
    ^
```

### Causa
Versión de Python muy antigua (< 3.7).

### Solución
```bash
# Verificar versión de Python
python --version

# Debe ser Python 3.8 o superior
# Si es menor, actualiza Python:

# macOS
brew install python@3.11

# Ubuntu/Debian
sudo apt update
sudo apt install python3.11

# Windows
# Descarga desde python.org
```

---

## 📦 Error al instalar dependencias

### Síntoma
```
ERROR: Could not find a version that satisfies the requirement...
```

### Solución

#### Opción 1: Actualizar pip
```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

#### Opción 2: Instalar una a una
```bash
pip install python-telegram-bot==20.7
pip install APScheduler==3.10.4
pip install python-dotenv==1.0.0
```

#### Opción 3: Usar Python 3.11
```bash
python3.11 -m pip install -r requirements.txt
python3.11 main.py
```

---

## 🔍 El bot se ejecuta pero da errores al presionar botones

### Síntoma
Al presionar botones, el bot no responde o da errores.

### Solución

#### 1. Verificar logs en consola
Busca mensajes de error cuando presionas un botón.

#### 2. Verificar que la base de datos tiene datos
```bash
# Ver si hay datos en la base de datos
sqlite3 productivity_bot.db
SELECT COUNT(*) FROM projects;
SELECT COUNT(*) FROM tasks;
.exit

# Si no hay datos, agregar datos de prueba
python add_sample_data.py
```

#### 3. Verificar permisos de archivo
```bash
# En Linux/Mac
chmod 644 productivity_bot.db
```

---

## 🌐 Error de red al instalar dependencias

### Síntoma
```
ReadTimeoutError: HTTPSConnectionPool
```

### Solución
```bash
# Aumentar timeout
pip install --default-timeout=100 -r requirements.txt

# O descargar manualmente
pip download python-telegram-bot==20.7
pip install python_telegram_bot-20.7-*.whl
```

---

## 🔒 Error: Permission denied

### Síntoma
```
PermissionError: [Errno 13] Permission denied: 'productivity_bot.db'
```

### Solución
```bash
# Linux/Mac
chmod 666 productivity_bot.db

# O ejecutar desde tu home directory
cd ~
mkdir telegram-bot
cd telegram-bot
# Copia archivos aquí
python main.py
```

---

## 📱 El bot responde lento

### Posibles causas

1. **Servidor saturado**: Si usas VPS compartido
2. **Muchos datos**: Miles de tareas/proyectos
3. **Red lenta**: Conexión a internet lenta

### Soluciones

1. **Optimizar base de datos**
   ```bash
   sqlite3 productivity_bot.db
   VACUUM;
   ANALYZE;
   .exit
   ```

2. **Limpiar datos antiguos**
   ```bash
   sqlite3 productivity_bot.db
   DELETE FROM tasks WHERE status = 'completed' AND date(completed_at) < date('now', '-3 months');
   .exit
   ```

3. **Usar servidor más rápido**

---

## 🧪 Cómo verificar que todo está bien

### Script de verificación completo
```bash
# 1. Verificar Python
python --version
# Debe mostrar 3.8 o superior

# 2. Verificar dependencias instaladas
pip list | grep telegram
pip list | grep APScheduler
# Deben aparecer

# 3. Verificar importaciones
python verify_imports.py
# Debe mostrar "✅ TODAS LAS IMPORTACIONES CORRECTAS"

# 4. Verificar base de datos
python add_sample_data.py
# Debe completarse sin errores

# 5. Iniciar bot
python main.py
# Debe mostrar:
# ✅ Base de datos inicializada
# ✅ Bot inicializado
# ✅ Handlers configurados
# ✅ Sistema de recordatorios configurado
# 🔄 Esperando mensajes...
```

---

## 🆘 Aún tengo problemas

Si ninguna solución funciona:

### 1. Revisar logs completos
```bash
# Ejecutar con logs detallados
python main.py 2>&1 | tee bot_error.log
```

### 2. Verificar versiones
```bash
python --version
pip list
```

### 3. Empezar de cero
```bash
# Eliminar todo
rm -rf database/ handlers/ utils/ *.db *.pyc __pycache__

# Descargar archivos frescos
# Volver a instalar dependencias
pip install -r requirements.txt

# Ejecutar
python main.py
```

### 4. Información del sistema
```bash
# Recopilar información para debug
python --version
pip list
uname -a  # Linux/Mac
systeminfo  # Windows
```

---

## ✅ Checklist de Verificación Rápida

Antes de reportar un problema, verifica:

- [ ] Python 3.8 o superior instalado
- [ ] Dependencias instaladas (`pip list`)
- [ ] Token correcto en `config.py`
- [ ] ID de usuario correcto en `config.py`
- [ ] Base de datos existe (`ls *.db`)
- [ ] Script de verificación pasa (`python verify_imports.py`)
- [ ] Bot ejecutándose (`python main.py` muestra "Esperando mensajes")
- [ ] Usuario correcto en Telegram (@glitchbane)

---

## 📞 Información Útil

**Tu configuración actual:**
- Bot: @fluxa_asistente_glitchbane_bot
- Token: 8222314009:AAG-nc-6_IJvVMk-LH4Q5bFVO3GLOymTA4o
- Usuario: @glitchbane (ID: 6009496370)
- Zona horaria: Europe/Madrid

**Versiones requeridas:**
- Python: >= 3.8
- python-telegram-bot: 20.7
- APScheduler: 3.10.4

---

💡 **Tip**: Guarda el output del comando `python main.py` en un archivo para revisar errores:
```bash
python main.py > bot.log 2>&1
```
