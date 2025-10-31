"""
Script de verificación de importaciones
Ejecuta este script para verificar que no hay errores de importación
"""

print("🔍 Verificando importaciones...")
print()

try:
    print("1️⃣ Importando config...")
    import config
    print("   ✅ config OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

try:
    print("2️⃣ Importando database...")
    from database.models import DatabaseManager, Project, Task, Note
    print("   ✅ database OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

try:
    print("3️⃣ Importando utils...")
    from utils.keyboards import get_main_keyboard
    from utils.formatters import format_dashboard
    from utils.reminders import ReminderSystem
    print("   ✅ utils OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

try:
    print("4️⃣ Importando handlers...")
    from handlers import menu
    print("   ✅ menu OK")
    from handlers import projects
    print("   ✅ projects OK")
    from handlers import tasks
    print("   ✅ tasks OK")
    from handlers import notes
    print("   ✅ notes OK")
    from handlers import dashboard
    print("   ✅ dashboard OK")
    from handlers import settings
    print("   ✅ settings OK")
    from handlers import task_conversations
    print("   ✅ task_conversations OK")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

print()
print("=" * 50)
print("✅ TODAS LAS IMPORTACIONES CORRECTAS")
print("=" * 50)
print()
print("El bot está listo para ejecutarse con:")
print("   python main.py")
print()
