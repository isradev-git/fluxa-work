# 🚀 INICIO RÁPIDO - 5 minutos

Esta guía te llevará de 0 a bot funcionando en 5 minutos.

## ⚡ Pasos Rápidos

### 1. Instalar dependencias (1 minuto)

```bash
cd telegram-bot
pip install -r requirements.txt
```

### 2. Agregar datos de prueba (30 segundos)

```bash
python add_sample_data.py
```

Esto creará:
- 3 proyectos de ejemplo
- 10 tareas (algunas completadas, otras pendientes)
- 5 notas con código y recursos

### 3. Iniciar el bot (10 segundos)

```bash
python main.py
```

Verás:
```
✅ Base de datos inicializada
✅ Bot inicializado
✅ Handlers configurados
✅ Sistema de recordatorios configurado
==================================================
✅ Bot de productividad iniciado correctamente
👤 Usuario autorizado: 6009496370
🔄 Esperando mensajes...
==================================================
```

### 4. Probar en Telegram (2 minutos)

1. Abre Telegram
2. Busca: `@fluxa_asistente_glitchbane_bot`
3. Envía: `/start`
4. ¡Usa los botones del menú!

## 🎯 Qué Probar Primero

### Ver Proyectos
1. Presiona **📁 Proyectos**
2. Presiona **📁 Ver proyectos activos**
3. Selecciona **"Landing Page Cliente Premium"**
4. Verás el progreso del proyecto con barra visual

### Ver Tareas de Hoy
1. Presiona **📅 Hoy**
2. Verás tareas con fecha límite hoy y atrasadas
3. Presiona una tarea para ver detalles

### Completar una Tarea
1. Presiona **✅ Tareas**
2. Presiona **📅 Tareas de hoy**
3. Selecciona una tarea
4. Presiona **✅ Completar**
5. ¡Tarea completada! 🎉

### Ver Dashboard
1. Presiona **📊 Dashboard**
2. Verás resumen completo de tu productividad
3. Presiona **📊 Estadísticas semanales** para ver más detalles

### Ver Notas
1. Presiona **📝 Notas**
2. Presiona **📝 Todas las notas**
3. Selecciona cualquier nota para leer su contenido

## 🔄 Flujo Típico de Uso

### Mañana (07:00)
```
🌅 Bot envía resumen diario automáticamente
    - Tareas de hoy
    - Tareas atrasadas  
    - Próximas entregas
```

### Durante el día
```
1. Abres el bot
2. Presionas "Tareas"
3. Ves tareas pendientes
4. Completas tareas con botones
5. Pospones lo que no puedes hacer hoy
```

### Tarde (18:00)
```
⏰ Bot te recuerda tareas con entrega mañana
```

### Fin de semana
```
📊 Bot envía resumen semanal el domingo
```

## 🧪 Probar Recordatorios

Los recordatorios están programados para horas específicas (07:00, 18:00).

Para **probar el resumen diario ahora mismo**:

```python
# Abre Python en otra terminal
python

# Ejecuta esto:
from utils.reminders import ReminderSystem
from database.models import DatabaseManager
from telegram import Bot
import asyncio
import config

db = DatabaseManager()
bot = Bot(token=config.BOT_TOKEN)
reminder = ReminderSystem(db, bot, config.AUTHORIZED_USER_ID)

# Enviar resumen diario ahora
asyncio.run(reminder.send_daily_summary())
```

## 📊 Ver la Base de Datos

Puedes ver directamente los datos con cualquier visor de SQLite:

```bash
# Instalar sqlite3 (si no lo tienes)
sudo apt install sqlite3  # Linux
brew install sqlite3      # Mac

# Ver datos
sqlite3 productivity_bot.db

# Comandos útiles dentro de SQLite:
.tables                    # Ver tablas
SELECT * FROM projects;    # Ver proyectos
SELECT * FROM tasks;       # Ver tareas
SELECT * FROM notes;       # Ver notas
.exit                      # Salir
```

## 🧹 Limpiar y Empezar de Cero

```bash
# Detener el bot (Ctrl+C)
# Eliminar base de datos
rm productivity_bot.db

# Reiniciar bot (creará nueva base de datos vacía)
python main.py
```

## ❓ Troubleshooting Rápido

### El bot no responde
```bash
# ¿Está ejecutándose?
# Deberías ver "🔄 Esperando mensajes..." en la terminal

# ¿Token correcto?
# Verifica config.py → BOT_TOKEN

# ¿ID correcto?
# Verifica config.py → AUTHORIZED_USER_ID
```

### Error al instalar dependencias
```bash
# Actualizar pip primero
python -m pip install --upgrade pip

# Intentar de nuevo
pip install -r requirements.txt
```

### Error de permisos
```bash
# Usar pip con --user
pip install --user -r requirements.txt
```

## 🎓 Siguientes Pasos

Una vez que hayas probado el bot:

1. **Lee RESUMEN_EJECUTIVO.md** para entender cómo funciona todo
2. **Lee README.md** para la guía completa
3. **Explora el código** (está todo comentado en español)
4. **Personaliza** horarios y configuración en `config.py`

## 💡 Tips Pro

- **Mantén el bot ejecutándose**: Usa `screen` o `tmux`
- **Backup regular**: Copia `productivity_bot.db` regularmente
- **Revisa logs**: El bot imprime mensajes útiles en la consola
- **Experimenta**: No tengas miedo de probar cosas

## 📞 Necesitas Ayuda?

- **Errores comunes**: Revisa la sección Troubleshooting del README.md
- **Entender código**: Lee los comentarios en los archivos .py
- **Aprender más**: Lee RESUMEN_EJECUTIVO.md con explicaciones detalladas

---

¡Listo! En 5 minutos deberías tener el bot funcionando. 🎉

**Comando para empezar AHORA:**
```bash
pip install -r requirements.txt && python add_sample_data.py && python main.py
```
