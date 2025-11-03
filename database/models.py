"""
Modelos de datos para el bot de productividad
Este archivo define las estructuras de datos que se guardarán en la base de datos SQLite
"""
import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import config

class DatabaseManager:
    """
    Gestor principal de la base de datos.
    Maneja la conexión y creación de tablas.
    """
    
    def __init__(self, db_path: str = config.DATABASE_PATH):
        """
        Inicializa el gestor de base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos SQLite
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        """Crea y retorna una nueva conexión a la base de datos"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Permite acceder a columnas por nombre
        return conn
    
    def init_database(self):
        """
        Crea todas las tablas necesarias si no existen.
        Se ejecuta al iniciar el bot por primera vez.
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabla de proyectos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                client TEXT,
                status TEXT DEFAULT 'active',
                priority TEXT DEFAULT 'medium',
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP
            )
        """)
        
        # Tabla de tareas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                project_id INTEGER,
                status TEXT DEFAULT 'pending',
                priority TEXT DEFAULT 'medium',
                deadline DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                parent_task_id INTEGER,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE,
                FOREIGN KEY (parent_task_id) REFERENCES tasks (id) ON DELETE CASCADE
            )
        """)
        
        # Tabla de notas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                project_id INTEGER,
                task_id INTEGER,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE SET NULL,
                FOREIGN KEY (task_id) REFERENCES tasks (id) ON DELETE SET NULL
            )
        """)
        
        # Tabla de configuración del usuario
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_settings (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                daily_summary_time TEXT DEFAULT '07:00',
                evening_reminder_time TEXT DEFAULT '18:00',
                timezone TEXT DEFAULT 'Europe/Madrid',
                daily_summary_enabled INTEGER DEFAULT 1,
                evening_reminder_enabled INTEGER DEFAULT 1
            )
        """)
        
        # Insertar configuración por defecto si no existe
        cursor.execute("""
            INSERT OR IGNORE INTO user_settings (id) VALUES (1)
        """)
        
        conn.commit()
        conn.close()


class Project:
    """
    Clase para gestionar proyectos.
    Un proyecto puede tener múltiples tareas asociadas.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create(self, name: str, description: str = "", client: str = "", 
               priority: str = "medium", deadline: Optional[str] = None) -> int:
        """
        Crea un nuevo proyecto.
        
        Args:
            name: Nombre del proyecto
            description: Descripción opcional
            client: Cliente asociado (opcional)
            priority: Prioridad (low, medium, high)
            deadline: Fecha límite en formato YYYY-MM-DD
            
        Returns:
            ID del proyecto creado
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO projects (name, description, client, priority, deadline)
            VALUES (?, ?, ?, ?, ?)
        """, (name, description, client, priority, deadline))
        
        project_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return project_id
    
    def get_all(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proyectos, opcionalmente filtrados por estado.
        
        Args:
            status: Filtrar por estado (active, paused, completed) o None para todos
            
        Returns:
            Lista de proyectos como diccionarios
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        if status:
            cursor.execute("""
                SELECT * FROM projects 
                WHERE status = ?
                ORDER BY 
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                    END,
                    deadline ASC
            """, (status,))
        else:
            cursor.execute("""
                SELECT * FROM projects 
                ORDER BY 
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                    END,
                    deadline ASC
            """)
        
        projects = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return projects
    
    def get_by_id(self, project_id: int) -> Optional[Dict[str, Any]]:
        """
        Obtiene un proyecto específico por su ID.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con datos del proyecto o None si no existe
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM projects WHERE id = ?", (project_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_status(self, task_id: int, status: str) -> bool:
        """
        Actualiza el estado de una tarea.
        
        Args:
            task_id: ID de la tarea
            status: Nuevo estado (pending, in_progress, completed)
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Validar que el estado sea uno de los permitidos
        valid_statuses = ['pending', 'in_progress', 'completed']
        if status not in valid_statuses:
            print(f"ERROR: Estado inválido '{status}'. Estados válidos: {valid_statuses}")
            conn.close()
            return False
        
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, 
                updated_at = CURRENT_TIMESTAMP,
                completed_at = ?
            WHERE id = ?
        """, (status, completed_at, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    def get_progress(self, project_id: int) -> Dict[str, Any]:
        """
        Calcula el progreso de un proyecto basándose en sus tareas.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas de progreso
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Contar tareas totales y completadas
        cursor.execute("""
            SELECT 
                COUNT(*) as total_tasks,
                SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed_tasks
            FROM tasks
            WHERE project_id = ?
        """, (project_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        total = result['total_tasks'] or 0
        completed = result['completed_tasks'] or 0
        
        percentage = (completed / total * 100) if total > 0 else 0
        
        return {
            'total_tasks': total,
            'completed_tasks': completed,
            'pending_tasks': total - completed,
            'percentage': round(percentage, 1)
        }
    
    def delete(self, project_id: int) -> bool:
        """
        Elimina un proyecto y todas sus tareas asociadas.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            True si se eliminó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM projects WHERE id = ?", (project_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success


class Task:
    """
    Clase para gestionar tareas.
    Las tareas pueden estar asociadas a proyectos y tener subtareas.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create(self, title: str, description: str = "", project_id: Optional[int] = None,
               priority: str = "medium", deadline: Optional[str] = None,
               parent_task_id: Optional[int] = None) -> int:
        """
        Crea una nueva tarea.
        
        Args:
            title: Título de la tarea
            description: Descripción opcional
            project_id: ID del proyecto asociado (opcional)
            priority: Prioridad (low, medium, high)
            deadline: Fecha límite en formato YYYY-MM-DD
            parent_task_id: ID de tarea padre (para subtareas)
            
        Returns:
            ID de la tarea creada
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tasks (title, description, project_id, priority, deadline, parent_task_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (title, description, project_id, priority, deadline, parent_task_id))
        
        task_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return task_id
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todas las tareas con filtros opcionales.
        
        Args:
            filters: Diccionario con filtros opcionales:
                - status: Estado de la tarea
                - project_id: ID del proyecto
                - priority: Prioridad
                - overdue: True para tareas atrasadas
                - today: True para tareas de hoy
                - parent_only: True para excluir subtareas
                
        Returns:
            Lista de tareas como diccionarios
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM tasks WHERE 1=1"
        params = []
        
        if filters:
            if 'status' in filters:
                query += " AND status = ?"
                params.append(filters['status'])
            
            if 'project_id' in filters:
                query += " AND project_id = ?"
                params.append(filters['project_id'])
            
            if 'priority' in filters:
                query += " AND priority = ?"
                params.append(filters['priority'])
            
            if filters.get('overdue'):
                query += " AND deadline < date('now') AND status != 'completed'"
            
            if filters.get('today'):
                query += " AND deadline = date('now') AND status != 'completed'"
            
            if filters.get('parent_only'):
                query += " AND parent_task_id IS NULL"
            
            # Nuevos filtros para fechas
            if 'deadline_from' in filters:
                query += " AND deadline >= ?"
                params.append(filters['deadline_from'])
            
            if 'deadline_to' in filters:
                query += " AND deadline <= ?"
                params.append(filters['deadline_to'])
        
        query += """ ORDER BY 
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
            END,
            deadline ASC
        """
        
        cursor.execute(query, params)
        tasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return tasks
    
    def get_by_id(self, task_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una tarea específica por su ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_status(self, task_id: int, status: str) -> bool:
        """
        Actualiza el estado de una tarea.
        
        Args:
            task_id: ID de la tarea
            status: Nuevo estado (pending, in_progress, completed)
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        completed_at = datetime.now().isoformat() if status == 'completed' else None
        
        cursor.execute("""
            UPDATE tasks 
            SET status = ?, 
                updated_at = CURRENT_TIMESTAMP,
                completed_at = ?
            WHERE id = ?
        """, (status, completed_at, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    # NUEVOS MÉTODOS AÑADIDOS
    
    def update_deadline(self, task_id: int, deadline: Optional[str]) -> bool:
        """
        Actualiza la fecha límite de una tarea.
        
        Args:
            task_id: ID de la tarea
            deadline: Nueva fecha límite en formato YYYY-MM-DD o None para sin fecha
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET deadline = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (deadline, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update_title(self, task_id: int, title: str) -> bool:
        """
        Actualiza el título de una tarea.
        
        Args:
            task_id: ID de la tarea
            title: Nuevo título
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET title = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (title, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update_description(self, task_id: int, description: str) -> bool:
        """
        Actualiza la descripción de una tarea.
        
        Args:
            task_id: ID de la tarea
            description: Nueva descripción
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET description = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (description, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update_priority(self, task_id: int, priority: str) -> bool:
        """
        Actualiza la prioridad de una tarea.
        
        Args:
            task_id: ID de la tarea
            priority: Nueva prioridad (low, medium, high)
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET priority = ?, 
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (priority, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def update(self, task_id: int, data: Dict[str, Any]) -> bool:
        """
        Actualiza múltiples campos de una tarea.
        
        Args:
            task_id: ID de la tarea
            data: Diccionario con los campos a actualizar
            
        Returns:
            True si se actualizó correctamente
        """
        if not data:
            return False
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        # Construir la consulta dinámicamente
        set_clause = ", ".join([f"{key} = ?" for key in data.keys()])
        values = list(data.values())
        values.append(task_id)
        
        cursor.execute(f"""
            UPDATE tasks 
            SET {set_clause}, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, values)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def postpone(self, task_id: int, days: int) -> bool:
        """
        Pospone una tarea X días.
        
        Args:
            task_id: ID de la tarea
            days: Número de días a posponer
            
        Returns:
            True si se actualizó correctamente
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            UPDATE tasks 
            SET deadline = date(deadline, '+' || ? || ' days'),
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (days, task_id))
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete(self, task_id: int) -> bool:
        """Elimina una tarea"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success
    
    def get_subtasks(self, parent_task_id: int) -> List[Dict[str, Any]]:
        """Obtiene las subtareas de una tarea padre"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM tasks 
            WHERE parent_task_id = ?
            ORDER BY created_at ASC
        """, (parent_task_id,))
        
        subtasks = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return subtasks


class Note:
    """
    Clase para gestionar notas.
    Las notas pueden asociarse a proyectos o tareas y organizarse por etiquetas.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def create(self, title: str, content: str, tags: str = "",
               project_id: Optional[int] = None, task_id: Optional[int] = None) -> int:
        """
        Crea una nueva nota.
        
        Args:
            title: Título de la nota
            content: Contenido de la nota
            tags: Etiquetas separadas por comas
            project_id: ID del proyecto asociado (opcional)
            task_id: ID de la tarea asociada (opcional)
            
        Returns:
            ID de la nota creada
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO notes (title, content, tags, project_id, task_id)
            VALUES (?, ?, ?, ?, ?)
        """, (title, content, tags, project_id, task_id))
        
        note_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        return note_id
    
    def get_all(self, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todas las notas con filtros opcionales.
        
        Args:
            filters: Diccionario con filtros opcionales:
                - project_id: ID del proyecto
                - task_id: ID de la tarea
                - tag: Buscar por etiqueta
                - search: Buscar en título y contenido
                
        Returns:
            Lista de notas como diccionarios
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM notes WHERE 1=1"
        params = []
        
        if filters:
            if 'project_id' in filters:
                query += " AND project_id = ?"
                params.append(filters['project_id'])
            
            if 'task_id' in filters:
                query += " AND task_id = ?"
                params.append(filters['task_id'])
            
            if 'tag' in filters:
                query += " AND tags LIKE ?"
                params.append(f"%{filters['tag']}%")
            
            if 'search' in filters:
                query += " AND (title LIKE ? OR content LIKE ?)"
                search_term = f"%{filters['search']}%"
                params.extend([search_term, search_term])
        
        query += " ORDER BY updated_at DESC"
        
        cursor.execute(query, params)
        notes = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return notes
    
    def get_by_id(self, note_id: int) -> Optional[Dict[str, Any]]:
        """Obtiene una nota específica por su ID"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM notes WHERE id = ?", (note_id,))
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update(self, note_id: int, title: Optional[str] = None, 
               content: Optional[str] = None, tags: Optional[str] = None) -> bool:
        """Actualiza los campos de una nota"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        updates = []
        params = []
        
        if title is not None:
            updates.append("title = ?")
            params.append(title)
        
        if content is not None:
            updates.append("content = ?")
            params.append(content)
        
        if tags is not None:
            updates.append("tags = ?")
            params.append(tags)
        
        if not updates:
            return False
        
        updates.append("updated_at = CURRENT_TIMESTAMP")
        params.append(note_id)
        
        query = f"UPDATE notes SET {', '.join(updates)} WHERE id = ?"
        cursor.execute(query, params)
        
        success = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return success
    
    def delete(self, note_id: int) -> bool:
        """Elimina una nota"""
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM notes WHERE id = ?", (note_id,))
        success = cursor.rowcount > 0
        
        conn.commit()
        conn.close()
        
        return success