"""
Script para agregar datos de prueba al bot
Ejecuta este archivo para llenar la base de datos con proyectos, tareas y notas de ejemplo
"""
from datetime import date, timedelta
from database.models import DatabaseManager, Project, Task, Note

def add_sample_data():
    """
    Agrega datos de prueba a la base de datos.
    Esto te permite probar el bot con información real.
    """
    print("🚀 Agregando datos de prueba...")
    
    # Inicializar gestores
    db = DatabaseManager()
    project_manager = Project(db)
    task_manager = Task(db)
    note_manager = Note(db)
    
    # Calcular fechas
    today = date.today()
    tomorrow = today + timedelta(days=1)
    next_week = today + timedelta(days=7)
    next_month = today + timedelta(days=30)
    last_week = today - timedelta(days=7)
    
    # ========== PROYECTOS ==========
    print("\n📁 Creando proyectos de prueba...")
    
    # Proyecto 1: Activo, alta prioridad
    project1_id = project_manager.create(
        name="Landing Page Cliente Premium",
        description="Rediseño completo de landing page con integración de pasarela de pago",
        client="Cliente Premium SL",
        priority="high",
        deadline=next_week.strftime("%Y-%m-%d")
    )
    print(f"✅ Proyecto 1 creado: ID {project1_id}")
    
    # Proyecto 2: Activo, prioridad media
    project2_id = project_manager.create(
        name="App de Gestión de Pedidos",
        description="Aplicación web para gestión de pedidos y clientes",
        client="Restaurante La Tasca",
        priority="medium",
        deadline=next_month.strftime("%Y-%m-%d")
    )
    print(f"✅ Proyecto 2 creado: ID {project2_id}")
    
    # Proyecto 3: Completado
    project3_id = project_manager.create(
        name="Blog Personal",
        description="Blog con CMS personalizado",
        client="Personal",
        priority="low",
        deadline=last_week.strftime("%Y-%m-%d")
    )
    project_manager.update_status(project3_id, 'completed')
    print(f"✅ Proyecto 3 creado (completado): ID {project3_id}")
    
    # ========== TAREAS ==========
    print("\n✅ Creando tareas de prueba...")
    
    # Tareas del Proyecto 1 (Landing Page)
    task1_id = task_manager.create(
        title="Configurar hosting y dominio",
        description="Contratar hosting en DigitalOcean y configurar DNS",
        project_id=project1_id,
        priority="high",
        deadline=today.strftime("%Y-%m-%d")
    )
    task_manager.update_status(task1_id, 'completed')
    print(f"✅ Tarea 1 creada: ID {task1_id}")
    
    task2_id = task_manager.create(
        title="Diseñar mockups en Figma",
        description="Crear diseño de la landing con los requisitos del cliente",
        project_id=project1_id,
        priority="high",
        deadline=tomorrow.strftime("%Y-%m-%d")
    )
    task_manager.update_status(task2_id, 'in_progress')
    print(f"✅ Tarea 2 creada: ID {task2_id}")
    
    task3_id = task_manager.create(
        title="Integrar pasarela de pago Stripe",
        description="Implementar checkout con Stripe API",
        project_id=project1_id,
        priority="high",
        deadline=(today + timedelta(days=3)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 3 creada: ID {task3_id}")
    
    task4_id = task_manager.create(
        title="Tests responsive en móvil",
        description="Probar diseño en iPhone, Android y tablets",
        project_id=project1_id,
        priority="medium",
        deadline=(today + timedelta(days=5)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 4 creada: ID {task4_id}")
    
    # Tareas del Proyecto 2 (App de Pedidos)
    task5_id = task_manager.create(
        title="Definir estructura de base de datos",
        description="Diseñar esquema para pedidos, clientes, productos",
        project_id=project2_id,
        priority="high",
        deadline=tomorrow.strftime("%Y-%m-%d")
    )
    task_manager.update_status(task5_id, 'in_progress')
    print(f"✅ Tarea 5 creada: ID {task5_id}")
    
    task6_id = task_manager.create(
        title="Crear API REST con FastAPI",
        description="Endpoints para CRUD de pedidos y autenticación",
        project_id=project2_id,
        priority="high",
        deadline=(today + timedelta(days=10)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 6 creada: ID {task6_id}")
    
    task7_id = task_manager.create(
        title="Desarrollar dashboard en React",
        description="Panel de administración con gráficos de ventas",
        project_id=project2_id,
        priority="medium",
        deadline=(today + timedelta(days=20)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 7 creada: ID {task7_id}")
    
    # Tareas sin proyecto (personales)
    task8_id = task_manager.create(
        title="Actualizar portfolio personal",
        description="Agregar últimos 3 proyectos al portfolio",
        priority="medium",
        deadline=(today + timedelta(days=7)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 8 creada: ID {task8_id}")
    
    task9_id = task_manager.create(
        title="Estudiar nuevas features de Python 3.12",
        description="Revisar documentación y hacer ejemplos",
        priority="low",
        deadline=(today + timedelta(days=14)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 9 creada: ID {task9_id}")
    
    # Tarea atrasada (para testing)
    task10_id = task_manager.create(
        title="Revisar facturación del mes pasado",
        description="Generar informe de ingresos y gastos",
        priority="high",
        deadline=(today - timedelta(days=2)).strftime("%Y-%m-%d")
    )
    print(f"✅ Tarea 10 creada (atrasada): ID {task10_id}")
    
    # Subtarea de ejemplo
    subtask1_id = task_manager.create(
        title="Investigar proveedores de Stripe",
        description="Comparar comisiones y features",
        parent_task_id=task3_id,
        priority="high",
        deadline=tomorrow.strftime("%Y-%m-%d")
    )
    task_manager.update_status(subtask1_id, 'completed')
    print(f"✅ Subtarea 1 creada: ID {subtask1_id}")
    
    # ========== NOTAS ==========
    print("\n📝 Creando notas de prueba...")
    
    note1_id = note_manager.create(
        title="Comandos útiles de Docker",
        content="""
Comandos Docker que uso frecuentemente:

docker ps -a  # Ver todos los contenedores
docker images  # Ver imágenes
docker-compose up -d  # Levantar servicios en background
docker logs -f [container]  # Ver logs en tiempo real
docker exec -it [container] bash  # Entrar al contenedor

Recordar siempre usar volumes para persistir datos!
        """,
        tags="docker,devops,comandos",
        project_id=project2_id
    )
    print(f"✅ Nota 1 creada: ID {note1_id}")
    
    note2_id = note_manager.create(
        title="Requisitos cliente Landing Page",
        content="""
Requisitos del cliente para la landing:

✅ Diseño minimalista y moderno
✅ Colores: azul (#0066CC) y blanco
✅ Secciones: Hero, Features, Pricing, Testimonios, FAQ, Contact
✅ Formulario de contacto con validación
✅ Integración con Stripe para pagos
✅ Certificado SSL incluido
✅ Optimizada para SEO
✅ Tiempo de carga < 2 segundos

Budget: 2500€
Fecha entrega: [fecha del proyecto]
        """,
        tags="cliente,requisitos,landing",
        project_id=project1_id
    )
    print(f"✅ Nota 2 creada: ID {note2_id}")
    
    note3_id = note_manager.create(
        title="Snippet: Autenticación JWT en FastAPI",
        content="""
```python
from fastapi import Depends, HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta

SECRET_KEY = "tu-secret-key-super-segura"
ALGORITHM = "HS256"

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=30)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload.get("sub")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
```

Notas: 
- Cambiar SECRET_KEY en producción
- Usar variables de entorno
- Considerar refresh tokens para sesiones largas
        """,
        tags="python,fastapi,jwt,auth,backend"
    )
    print(f"✅ Nota 3 creada: ID {note3_id}")
    
    note4_id = note_manager.create(
        title="Ideas para mejorar workflow",
        content="""
Ideas para optimizar mi flujo de trabajo:

1. Implementar CI/CD con GitHub Actions
2. Usar Tailwind CSS en lugar de CSS vanilla (más rápido)
3. Configurar linter y formatter automático (Black + Flake8)
4. Crear templates reutilizables para proyectos
5. Documentar mejor el código con docstrings
6. Hacer backups automáticos semanales
7. Crear scripts de deployment automático

Prioridad: 1, 3, 5
        """,
        tags="workflow,productividad,ideas"
    )
    print(f"✅ Nota 4 creada: ID {note4_id}")
    
    note5_id = note_manager.create(
        title="Recursos de aprendizaje - FastAPI",
        content="""
Recursos útiles para dominar FastAPI:

📚 Documentación oficial: https://fastapi.tiangolo.com/
📺 Tutorial completo: "FastAPI - The Complete Course" (freeCodeCamp)
📝 Real Python - FastAPI tutorials
🎓 Curso Udemy: "FastAPI - The Complete Course 2024"

Temas a estudiar:
- Dependency Injection
- Background tasks
- WebSockets
- Testing con pytest
- Deployment con Docker + Nginx

Next: Hacer proyecto personal con FastAPI + React
        """,
        tags="aprendizaje,fastapi,python,recursos"
    )
    print(f"✅ Nota 5 creada: ID {note5_id}")
    
    # ========== RESUMEN ==========
    print("\n" + "="*50)
    print("✅ DATOS DE PRUEBA AGREGADOS CON ÉXITO")
    print("="*50)
    print(f"\n📊 Resumen:")
    print(f"   📁 Proyectos creados: 3 (2 activos, 1 completado)")
    print(f"   ✅ Tareas creadas: 10 (2 completadas, 2 en progreso, 6 pendientes)")
    print(f"   📝 Notas creadas: 5")
    print(f"\n💡 Ahora puedes:")
    print(f"   1. Iniciar el bot: python main.py")
    print(f"   2. Abrir Telegram y enviar /start a tu bot")
    print(f"   3. Explorar los proyectos, tareas y notas de prueba")
    print(f"\n🗑️  Para limpiar los datos de prueba:")
    print(f"   rm productivity_bot.db")
    print(f"   (Al reiniciar el bot se creará una nueva base de datos vacía)\n")


if __name__ == "__main__":
    add_sample_data()
