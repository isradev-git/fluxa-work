"""
Sistema de recordatorios automáticos
Este módulo maneja el envío programado de resúmenes diarios y recordatorios
"""
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
from telegram import Bot
from telegram.constants import ParseMode
import config
from database.models import DatabaseManager, Task, Project
from utils.formatters import format_daily_summary
from utils.keyboards import get_main_keyboard

class ReminderSystem:
    """
    Sistema que gestiona los recordatorios automáticos del bot.
    Envía el resumen diario cada mañana y recordatorios de tarde.
    """
    
    def __init__(self, db_manager: DatabaseManager, bot: Bot, user_id: int):
        """
        Inicializa el sistema de recordatorios.
        
        Args:
            db_manager: Instancia del gestor de base de datos
            bot: Instancia del bot de Telegram
            user_id: ID del usuario que recibirá los recordatorios
        """
        self.db = db_manager
        self.bot = bot
        self.user_id = user_id
        self.task_manager = Task(db_manager)
        self.project_manager = Project(db_manager)
    
    async def send_daily_summary(self):
        """
        Envía el resumen diario al usuario.
        Se ejecuta automáticamente a la hora configurada (por defecto 07:00).
        
        Esta función recopila:
        - Tareas con fecha límite para hoy
        - Tareas atrasadas
        - Próximas entregas de proyectos (en los próximos 7 días)
        - Número de proyectos activos
        """
        try:
            today = date.today()
            next_week = today + timedelta(days=7)
            
            # Obtener tareas de hoy
            tasks_today = self.task_manager.get_all({
                'today': True,
                'parent_only': True  # Solo tareas principales, no subtareas
            })
            
            # Obtener tareas atrasadas
            tasks_overdue = self.task_manager.get_all({
                'overdue': True,
                'parent_only': True
            })
            
            # Obtener proyectos con entregas próximas (7 días)
            all_projects = self.project_manager.get_all(status='active')
            upcoming_deadlines = []
            
            for project in all_projects:
                if project.get('deadline'):
                    try:
                        deadline = datetime.strptime(project['deadline'], "%Y-%m-%d").date()
                        if today <= deadline <= next_week:
                            upcoming_deadlines.append(project)
                    except:
                        continue
            
            # Ordenar por fecha de entrega
            upcoming_deadlines.sort(key=lambda x: x['deadline'])
            
            # Contar proyectos activos
            active_projects = len(all_projects)
            
            # Formatear mensaje
            message = format_daily_summary(
                tasks_today=tasks_today,
                tasks_overdue=tasks_overdue,
                upcoming_deadlines=upcoming_deadlines,
                active_projects=active_projects
            )
            
            # Enviar mensaje con teclado principal
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=ParseMode.HTML,
                reply_markup=get_main_keyboard()
            )
            
            print(f"✅ Resumen diario enviado a las {datetime.now().strftime('%H:%M')}")
            
        except Exception as e:
            print(f"❌ Error al enviar resumen diario: {e}")
    
    async def send_evening_reminder(self):
        """
        Envía recordatorio de tarde si hay tareas con entrega para mañana.
        Se ejecuta automáticamente a la hora configurada (por defecto 18:00).
        
        Este recordatorio solo se envía si hay tareas pendientes
        con fecha límite para el día siguiente.
        """
        try:
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime("%Y-%m-%d")
            
            # Obtener tareas con entrega mañana
            conn = self.db.get_connection()
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT * FROM tasks 
                WHERE deadline = ? 
                AND status != 'completed'
                AND parent_task_id IS NULL
                ORDER BY 
                    CASE priority
                        WHEN 'high' THEN 1
                        WHEN 'medium' THEN 2
                        WHEN 'low' THEN 3
                    END
            """, (tomorrow_str,))
            
            tasks_tomorrow = [dict(row) for row in cursor.fetchall()]
            conn.close()
            
            # Solo enviar si hay tareas
            if tasks_tomorrow:
                lines = [
                    f"⏰ <b>Recordatorio de tarde</b>",
                    f"",
                    f"Tienes <b>{len(tasks_tomorrow)}</b> tarea(s) con entrega mañana:",
                    f""
                ]
                
                for i, task in enumerate(tasks_tomorrow[:5], 1):
                    priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                    status = "🔄" if task['status'] == 'in_progress' else "⏳"
                    lines.append(f"{i}. {status}{priority} {task['title']}")
                
                if len(tasks_tomorrow) > 5:
                    lines.append(f"... y {len(tasks_tomorrow) - 5} más")
                
                lines.append("")
                lines.append("💪 ¡Aprovecha la tarde para adelantar trabajo!")
                
                message = "\n".join(lines)
                
                await self.bot.send_message(
                    chat_id=self.user_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
                
                print(f"✅ Recordatorio de tarde enviado: {len(tasks_tomorrow)} tareas para mañana")
            else:
                print(f"ℹ️ No hay tareas para mañana, recordatorio no enviado")
                
        except Exception as e:
            print(f"❌ Error al enviar recordatorio de tarde: {e}")
    
    async def send_weekly_summary(self):
        """
        Envía el resumen semanal con estadísticas.
        Se ejecuta automáticamente cada domingo por la noche.
        """
        try:
            # Calcular rango de la semana (lunes a domingo)
            today = date.today()
            # Retroceder al lunes de esta semana
            days_since_monday = today.weekday()  # 0 = lunes, 6 = domingo
            week_start = today - timedelta(days=days_since_monday)
            week_end = week_start + timedelta(days=6)
            
            # Obtener estadísticas
            stats = self._calculate_weekly_stats(week_start, week_end)
            
            # Formatear mensaje
            from utils.formatters import format_weekly_stats
            message = format_weekly_stats(stats)
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            print(f"✅ Resumen semanal enviado")
            
        except Exception as e:
            print(f"❌ Error al enviar resumen semanal: {e}")
    
    def _calculate_weekly_stats(self, week_start: date, week_end: date) -> Dict[str, Any]:
        """
        Calcula las estadísticas de una semana.
        
        Args:
            week_start: Fecha de inicio de la semana
            week_end: Fecha de fin de la semana
            
        Returns:
            Diccionario con estadísticas de la semana
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        week_start_str = week_start.strftime("%Y-%m-%d")
        week_end_str = week_end.strftime("%Y-%m-%d")
        
        # Tareas creadas en la semana
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks
            WHERE date(created_at) BETWEEN ? AND ?
        """, (week_start_str, week_end_str))
        tasks_created = cursor.fetchone()['count']
        
        # Tareas completadas en la semana
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks
            WHERE date(completed_at) BETWEEN ? AND ?
        """, (week_start_str, week_end_str))
        tasks_completed = cursor.fetchone()['count']
        
        # Tareas atrasadas
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks
            WHERE deadline < ? AND status != 'completed'
        """, (week_end_str,))
        tasks_overdue = cursor.fetchone()['count']
        
        # Calcular tasa de cumplimiento
        if tasks_created > 0:
            completion_rate = round((tasks_completed / tasks_created) * 100, 1)
        else:
            completion_rate = 0
        
        # Media diaria
        daily_average = round(tasks_completed / 7, 1)
        
        # Progreso de proyectos activos
        cursor.execute("""
            SELECT id, name FROM projects WHERE status = 'active'
        """)
        active_projects = cursor.fetchall()
        
        project_progress = []
        for project in active_projects:
            progress = self.project_manager.get_progress(project['id'])
            project_progress.append({
                'name': project['name'],
                'progress': progress['percentage']
            })
        
        conn.close()
        
        return {
            'week_start': week_start.strftime("%d/%m"),
            'week_end': week_end.strftime("%d/%m"),
            'tasks_created': tasks_created,
            'tasks_completed': tasks_completed,
            'tasks_overdue': tasks_overdue,
            'completion_rate': completion_rate,
            'daily_average': daily_average,
            'project_progress': project_progress
        }
    
    async def send_monthly_summary(self):
        """
        Envía el resumen mensual con estadísticas completas.
        Se ejecuta automáticamente el primer día de cada mes.
        """
        try:
            # Calcular mes anterior
            today = date.today()
            # Primer día del mes actual
            first_day_current = today.replace(day=1)
            # Último día del mes anterior
            last_day_previous = first_day_current - timedelta(days=1)
            # Primer día del mes anterior
            first_day_previous = last_day_previous.replace(day=1)
            
            # Obtener estadísticas
            stats = self._calculate_monthly_stats(first_day_previous, last_day_previous)
            
            # Formatear mensaje
            from utils.formatters import format_monthly_stats
            message = format_monthly_stats(stats)
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            print(f"✅ Resumen mensual enviado")
            
        except Exception as e:
            print(f"❌ Error al enviar resumen mensual: {e}")
    
    def _calculate_monthly_stats(self, month_start: date, month_end: date) -> Dict[str, Any]:
        """
        Calcula las estadísticas de un mes.
        
        Args:
            month_start: Primer día del mes
            month_end: Último día del mes
            
        Returns:
            Diccionario con estadísticas del mes
        """
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        month_start_str = month_start.strftime("%Y-%m-%d")
        month_end_str = month_end.strftime("%Y-%m-%d")
        
        # Tareas creadas
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks
            WHERE date(created_at) BETWEEN ? AND ?
        """, (month_start_str, month_end_str))
        tasks_created = cursor.fetchone()['count']
        
        # Tareas completadas
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks
            WHERE date(completed_at) BETWEEN ? AND ?
        """, (month_start_str, month_end_str))
        tasks_completed = cursor.fetchone()['count']
        
        # Tareas completadas a tiempo (antes de su deadline)
        cursor.execute("""
            SELECT COUNT(*) as count FROM tasks
            WHERE date(completed_at) BETWEEN ? AND ?
            AND date(completed_at) <= date(deadline)
        """, (month_start_str, month_end_str))
        tasks_on_time = cursor.fetchone()['count']
        
        # Tasa de puntualidad
        if tasks_completed > 0:
            on_time_rate = round((tasks_on_time / tasks_completed) * 100, 1)
        else:
            on_time_rate = 0
        
        # Proyectos completados
        cursor.execute("""
            SELECT COUNT(*) as count FROM projects
            WHERE date(completed_at) BETWEEN ? AND ?
        """, (month_start_str, month_end_str))
        projects_completed = cursor.fetchone()['count']
        
        # Proyectos activos al final del mes
        cursor.execute("""
            SELECT COUNT(*) as count FROM projects
            WHERE status = 'active'
        """)
        projects_active = cursor.fetchone()['count']
        
        # Distribución por prioridad
        cursor.execute("""
            SELECT priority, COUNT(*) as count FROM tasks
            WHERE date(created_at) BETWEEN ? AND ?
            GROUP BY priority
        """, (month_start_str, month_end_str))
        
        priority_dist = {row['priority']: row['count'] for row in cursor.fetchall()}
        
        conn.close()
        
        # Nombres de meses en español
        month_names = [
            '', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        # Tareas atrasadas actuales
        tasks_overdue = len(self.task_manager.get_all({'overdue': True}))
        
        return {
            'month_name': month_names[month_start.month],
            'year': month_start.year,
            'tasks_created': tasks_created,
            'tasks_completed': tasks_completed,
            'tasks_overdue': tasks_overdue,
            'on_time_rate': on_time_rate,
            'projects_completed': projects_completed,
            'projects_active': projects_active,
            'priority_high': priority_dist.get('high', 0),
            'priority_medium': priority_dist.get('medium', 0),
            'priority_low': priority_dist.get('low', 0)
        }
