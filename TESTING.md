# 🧪 GUÍA DE TESTING - Funcionalidades del Bot

Esta guía te ayuda a probar todas las funcionalidades del bot de forma ordenada.

---

## ✅ TAREAS - Funcionalidades

### 1. ✅ Nueva Tarea (IMPLEMENTADO)

**Cómo probar:**
1. Presiona **✅ Tareas**
2. Presiona **➕ Nueva tarea**
3. Sigue el diálogo paso a paso:
   - **Paso 1**: Escribe el título (ej: "Implementar login")
   - **Paso 2**: Escribe descripción o "-" para omitir
   - **Paso 3**: Selecciona prioridad (Alta/Media/Baja)
   - **Paso 4**: Escribe fecha límite:
     - `2024-12-31` (formato YYYY-MM-DD)
     - `hoy` (para hoy)
     - `mañana` (para mañana)
     - `+3` (para dentro de 3 días)
     - `-` (sin fecha)
   - **Paso 5** (opcional): Selecciona proyecto o "Sin proyecto"
4. Confirma la creación

**Resultado esperado:**
```
🎉 ¡Tarea creada con éxito!
✅ [Título de tu tarea]
ID de tarea: X
```

**Opciones después:**
- Ver tarea creada
- Crear nueva tarea
- Ver todas las tareas

---

### 2. ✅ Ver Tareas de Hoy

**Cómo probar:**
1. Presiona **✅ Tareas**
2. Presiona **📅 Tareas de hoy**

**Resultado esperado:**
- Lista de tareas con fecha límite para hoy
- Cada tarea muestra: estado, prioridad, título

---

### 3. ✅ Ver Tareas de Esta Semana

**Cómo probar:**
1. Presiona **✅ Tareas**
2. Presiona **📅 Esta semana**

**Resultado esperado:**
- Lista de tareas con fecha límite en los próximos 7 días

---

### 4. ✅ Ver Tareas Atrasadas

**Cómo probar:**
1. Presiona **✅ Tareas**
2. Presiona **⚠️ Atrasadas**

**Resultado esperado:**
- Lista de tareas con fecha límite pasada
- Muestra días de atraso

---

### 5. ✅ Ver Tareas Alta Prioridad

**Cómo probar:**
1. Presiona **✅ Tareas**
2. Presiona **🔴 Alta prioridad**

**Resultado esperado:**
- Solo tareas marcadas como alta prioridad

---

### 6. ✅ Ver Todas las Tareas

**Cómo probar:**
1. Presiona **✅ Tareas**
2. Presiona **✅ Todas las tareas**

**Resultado esperado:**
- Lista completa de tareas
- Muestra total, completadas, en progreso, pendientes

---

### 7. ✅ Ver Detalle de Tarea

**Cómo probar:**
1. Entra a cualquier lista de tareas
2. Presiona sobre una tarea específica

**Resultado esperado:**
- Título, descripción, estado, prioridad
- Fecha límite
- Proyecto asociado (si tiene)
- Fecha de creación
- Botones de acciones

---

### 8. ✅ Completar Tarea

**Cómo probar:**
1. Abre detalle de una tarea pendiente
2. Presiona **✅ Completar**

**Resultado esperado:**
- Mensaje: "¡Tarea completada! Buen trabajo"
- Estado cambia a "✅ Completada"
- Se registra fecha de finalización

---

### 9. ✅ Cambiar Estado a "En Progreso"

**Cómo probar:**
1. Abre detalle de una tarea pendiente
2. Presiona **▶️ En progreso**

**Resultado esperado:**
- Estado cambia a "🔄 En progreso"

---

### 10. ✅ Posponer Tarea

**Cómo probar:**
1. Abre detalle de una tarea con fecha límite
2. Presiona uno de:
   - **📅+1 día**
   - **📅+2 días**
   - **📅+1 semana**

**Resultado esperado:**
- Mensaje: "Tarea pospuesta X días"
- Fecha límite actualizada

---

### 11. ❌ Editar Tarea (PENDIENTE)

**Estado:** No implementado aún
**Requiere:** ConversationHandler similar a crear tarea

---

### 12. ❌ Eliminar Tarea (PENDIENTE)

**Estado:** No implementado aún
**Requiere:** Confirmación con botones

---

### 13. ✅ Reabrir Tarea Completada

**Cómo probar:**
1. Abre una tarea completada
2. Presiona **🔄 Reabrir tarea**

**Resultado esperado:**
- Estado vuelve a "⏳ Pendiente"

---

## 📊 RESUMEN DE TAREAS

| Funcionalidad | Estado | Comentario |
|--------------|--------|------------|
| ➕ Nueva tarea | ✅ FUNCIONA | Diálogo completo implementado |
| 📅 Tareas de hoy | ✅ FUNCIONA | - |
| 📅 Esta semana | ✅ FUNCIONA | - |
| ⚠️ Atrasadas | ✅ FUNCIONA | - |
| 🔴 Alta prioridad | ✅ FUNCIONA | - |
| 📋 Todas | ✅ FUNCIONA | Con paginación |
| 👁️ Ver detalle | ✅ FUNCIONA | - |
| ✅ Completar | ✅ FUNCIONA | - |
| 🔄 En progreso | ✅ FUNCIONA | - |
| 📅 Posponer | ✅ FUNCIONA | 1 día, 2 días, 1 semana |
| 🔄 Reabrir | ✅ FUNCIONA | - |
| ✏️ Editar | ❌ PENDIENTE | Por implementar |
| 🗑️ Eliminar | ❌ PENDIENTE | Por implementar |
| 📋 Subtareas | ❌ PENDIENTE | Ver/crear subtareas |

---

## 🧪 ESCENARIOS DE PRUEBA COMPLETOS

### Escenario 1: Crear y completar tarea simple
```
1. Tareas → Nueva tarea
2. Título: "Probar el bot"
3. Descripción: "-"
4. Prioridad: Alta
5. Fecha: mañana
6. Proyecto: Sin proyecto
7. Crear → Ver tarea → Completar
```

### Escenario 2: Crear tarea con todos los datos
```
1. Tareas → Nueva tarea
2. Título: "Implementar API de usuarios"
3. Descripción: "Endpoints CRUD con autenticación JWT"
4. Prioridad: Alta
5. Fecha: +7
6. Proyecto: Seleccionar uno existente
7. Crear
```

### Escenario 3: Gestionar tarea atrasada
```
1. Crear tarea con fecha de ayer
2. Tareas → Atrasadas
3. Abrir tarea
4. Posponer +2 días
5. Verificar que ya no aparece en atrasadas
```

### Escenario 4: Workflow completo
```
1. Crear tarea → Estado: Pendiente
2. Marcar en progreso → Estado: En progreso
3. Completar → Estado: Completada
4. Reabrir → Estado: Pendiente
```

---

## 📁 PROYECTOS - Por Probar

### Funcionalidades disponibles:
- [ ] Ver proyectos activos
- [ ] Ver proyecto con progreso
- [ ] Cambiar estado (activo/pausado)
- [ ] Completar proyecto
- [ ] Ver tareas del proyecto
- [ ] Ver proyectos finalizados

### No implementado:
- [ ] Crear proyecto (requiere ConversationHandler)
- [ ] Editar proyecto
- [ ] Eliminar proyecto

---

## 📝 NOTAS - Por Probar

### Funcionalidades disponibles:
- [ ] Ver todas las notas
- [ ] Ver detalle de nota
- [ ] Lista con paginación

### No implementado:
- [ ] Crear nota (requiere ConversationHandler)
- [ ] Editar nota
- [ ] Eliminar nota
- [ ] Buscar por etiquetas

---

## 📊 DASHBOARD - Por Probar

### Funcionalidades disponibles:
- [ ] Ver resumen general
- [ ] Estadísticas semanales
- [ ] Estadísticas mensuales
- [ ] Próximas entregas

---

## 📅 HOY - Por Probar

### Funcionalidades disponibles:
- [ ] Tareas de hoy
- [ ] Tareas atrasadas
- [ ] Mensaje motivacional

---

## ⚙️ CONFIGURACIÓN - Por Probar

### Funcionalidades disponibles:
- [ ] Ver menú de configuración

### No implementado:
- [ ] Cambiar horario de resumen
- [ ] Cambiar zona horaria
- [ ] Activar/desactivar recordatorios
- [ ] Exportar datos

---

## 🔔 RECORDATORIOS - Por Probar

### A probar (requieren tiempo):
- [ ] Resumen diario (07:00)
- [ ] Recordatorio tarde (18:00)
- [ ] Resumen semanal (Domingos)
- [ ] Resumen mensual (Día 1)

### Cómo probar ahora:
```python
# En terminal Python
from utils.reminders import ReminderSystem
from database.models import DatabaseManager
from telegram import Bot
import asyncio
import config

db = DatabaseManager()
bot = Bot(token=config.BOT_TOKEN)
reminder = ReminderSystem(db, bot, config.AUTHORIZED_USER_ID)

# Enviar resumen ahora
asyncio.run(reminder.send_daily_summary())
```

---

## 📋 CHECKLIST COMPLETO

### ✅ Funcionalidades Funcionando (16)
- [x] Menú principal
- [x] Nueva tarea
- [x] Ver tareas (hoy, semana, atrasadas, alta prioridad, todas)
- [x] Detalle de tarea
- [x] Completar tarea
- [x] Cambiar estado tarea
- [x] Posponer tarea
- [x] Reabrir tarea
- [x] Ver proyectos
- [x] Detalle de proyecto con progreso
- [x] Cambiar estado proyecto
- [x] Ver notas
- [x] Dashboard
- [x] Estadísticas

### ⏳ Por Implementar (12)
- [ ] Crear proyecto
- [ ] Editar proyecto/tarea/nota
- [ ] Eliminar con confirmación
- [ ] Crear nota
- [ ] Buscar por texto
- [ ] Filtros avanzados
- [ ] Configuración horarios
- [ ] Exportar datos
- [ ] Subtareas
- [ ] Adjuntar archivos

---

## 🐛 REGISTRO DE BUGS

### Durante Testing
Anota aquí cualquier bug encontrado:

**Ejemplo:**
```
[FECHA] [FUNCIONALIDAD]
Descripción: ...
Pasos para reproducir: ...
Comportamiento esperado: ...
Comportamiento actual: ...
```

---

## 💡 MEJORAS SUGERIDAS

Anota aquí ideas de mejora durante el testing:

**Ejemplo:**
```
- Agregar filtro por múltiples prioridades
- Mostrar % de progreso en lista de tareas
- Añadir búsqueda por texto en tareas
```

---

## ✅ ESTADO ACTUAL

**Última actualización:** 2024-10-29

**Funcionalidad probada:** Creación de tareas ✅

**Próximo a probar:** Resto de funcionalidades de tareas

---

¿Encontraste algún bug? Anótalo arriba y vuelve a probar después de corregirlo.
