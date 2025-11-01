"""
Sistema de recordatorios automáticos con personalidad Cortana
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
from cortana_personality import (
    CORTANA_DAILY_SUMMARY_INTRO,
    CORTANA_EVENING_REMINDER,
    CORTANA_WEEKLY_SUMMARY,
    CORTANA_MONTHLY_SUMMARY
)

class ReminderSystem:
    """
    Sistema que gestiona los recordatorios automáticos del bot con personalidad Cortana
    """
    
    def __init__(self, db_manager: DatabaseManager, bot: Bot, user_id: int):
        self.db = db_manager
        self.bot = bot
        self.user_id = user_id
        self.task_manager = Task(db_manager)
        self.project_manager = Project(db_manager)
    
    async def send_daily_summary(self):
        """Envía el briefing matutino al usuario"""
        try:
            today = date.today()
            
            tasks_today = self.task_manager.get_all({'today': True})
            tasks_overdue = self.task_manager.get_all({'overdue': True})
            
            active_projects = self.project_manager.get_all(status='active')
            
            next_week = today + timedelta(days=7)
            upcoming_deadlines = []
            for project in active_projects:
                if project.get('deadline'):
                    try:
                        deadline = datetime.strptime(project['deadline'], "%Y-%m-%d").date()
                        if today <= deadline <= next_week:
                            upcoming_deadlines.append(project)
                    except:
                        continue
            
            upcoming_deadlines.sort(key=lambda x: x['deadline'])
            
            lines = [
                CORTANA_DAILY_SUMMARY_INTRO,
                ""
            ]
            
            lines.append(f"📊 <b>Estado Táctico General</b>")
            lines.append(f"📁 Misiones activas: {len(active_projects)}")
            lines.append(f"📅 Objetivos de hoy: {len(tasks_today)}")
            lines.append(f"⚠️ Objetivos atrasados: {len(tasks_overdue)}")
            lines.append("")
            
            if tasks_today:
                lines.append(f"<b>📅 Objetivos para hoy:</b>")
                for i, task in enumerate(tasks_today[:5], 1):
                    priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                    lines.append(f"{i}. {priority} {task['title']}")
                
                if len(tasks_today) > 5:
                    lines.append(f"... y {len(tasks_today) - 5} más")
                lines.append("")
            
            if tasks_overdue:
                lines.append(f"<b>⚠️ Objetivos Atrasados:</b>")
                for i, task in enumerate(tasks_overdue[:3], 1):
                    priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                    days_overdue = (today - datetime.strptime(task['deadline'], "%Y-%m-%d").date()).days
                    lines.append(f"{i}. {priority} {task['title']} ({days_overdue} días de retraso)")
                
                if len(tasks_overdue) > 3:
                    lines.append(f"... y {len(tasks_overdue) - 3} más")
                lines.append("")
            
            if upcoming_deadlines:
                lines.append(f"<b>⏰ Próximos Deadlines (7 días):</b>")
                for i, project in enumerate(upcoming_deadlines[:3], 1):
                    from utils.formatters import format_date
                    lines.append(f"{i}. {project['name']} - {format_date(project['deadline'])}")
                
                if len(upcoming_deadlines) > 3:
                    lines.append(f"... y {len(upcoming_deadlines) - 3} más")
                lines.append("")
            
            if not tasks_today and not tasks_overdue:
                lines.append(f"✨ Día despejado. Perfecto para planificar o avanzar proyectos.")
            elif tasks_overdue:
                lines.append(f"💪 Tiempo de ponerse al día. Los datos no mienten.")
            else:
                lines.append(f"🚀 Todo listo para un día productivo. Vamos a ello, Spartan.")
            
            message = "\n".join(lines)
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            print(f"✅ Briefing matutino enviado")
            
        except Exception as e:
            print(f"❌ Error al enviar briefing: {e}")
    
    async def send_evening_reminder(self):
        """Envía el preview nocturno"""
        try:
            tomorrow = date.today() + timedelta(days=1)
            tomorrow_str = tomorrow.strftime("%Y-%m-%d")
            
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
            
            if tasks_tomorrow:
                lines = [
                    CORTANA_EVENING_REMINDER,
                    ""
                ]
                
                lines.append(f"Tienes <b>{len(tasks_tomorrow)}</b> objetivo(s) con deadline mañana:")
                lines.append("")
                
                for i, task in enumerate(tasks_tomorrow[:5], 1):
                    priority = "🔴" if task['priority'] == 'high' else "🟡" if task['priority'] == 'medium' else "🟢"
                    status = "🔄" if task['status'] == 'in_progress' else "⏳"
                    lines.append(f"{i}. {status}{priority} {task['title']}")
                
                if len(tasks_tomorrow) > 5:
                    lines.append(f"... y {len(tasks_tomorrow) - 5} más")
                
                lines.append("")
                lines.append("Sugerencia: Revisa si necesitas ajustar prioridades.")
                
                message = "\n".join(lines)
                
                await self.bot.send_message(
                    chat_id=self.user_id,
                    text=message,
                    parse_mode=ParseMode.HTML
                )
                
                print(f"✅ Preview nocturno enviado: {len(tasks_tomorrow)} objetivos para mañana")
            else:
                print(f"ℹ️ No hay objetivos para mañana, preview no enviado")
                
        except Exception as e:
            print(f"❌ Error al enviar preview nocturno: {e}")
    
    async def send_weekly_summary(self):
        """Envía el análisis semanal con estadísticas"""
        try:
            stats = self._calculate_weekly_stats()
            
            lines = [
                CORTANA_WEEKLY_SUMMARY,
                ""
            ]
            
            lines.append(f"📊 <b>Resumen de la Semana</b>")
            lines.append(f"")
            lines.append(f"✅ Objetivos completados: {stats['completed']}")
            lines.append(f"🔄 En progreso: {stats['in_progress']}")
            lines.append(f"⏳ Pendientes: {stats['pending']}")
            lines.append(f"")
            
            if stats['completed'] > 0:
                lines.append(f"📈 Tasa de finalización: {stats['completion_rate']}%")
                lines.append("")
            
            if stats['completed'] >= 10:
                lines.append("💪 Excelente rendimiento esta semana. Sigue así.")
            elif stats['completed'] >= 5:
                lines.append("👍 Buen progreso. Mantén el ritmo.")
            else:
                lines.append("📋 Considera revisar tus prioridades para la próxima semana.")
            
            message = "\n".join(lines)
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            print(f"✅ Análisis semanal enviado")
            
        except Exception as e:
            print(f"❌ Error al enviar análisis semanal: {e}")
    
    async def send_monthly_summary(self):
        """Envía el informe mensual con estadísticas"""
        try:
            stats = self._calculate_monthly_stats()
            
            lines = [
                CORTANA_MONTHLY_SUMMARY,
                ""
            ]
            
            last_month = (date.today().replace(day=1) - timedelta(days=1)).strftime("%B %Y")
            
            lines.append(f"📊 <b>Informe de {last_month}</b>")
            lines.append("")
            lines.append(f"✅ Objetivos completados: {stats['completed']}")
            lines.append(f"📁 Misiones finalizadas: {stats['projects_completed']}")
            lines.append(f"📈 Productividad: {stats['productivity_score']}/10")
            lines.append("")
            
            if stats['productivity_score'] >= 8:
                lines.append("🌟 Mes excepcional. Los números lo confirman.")
            elif stats['productivity_score'] >= 6:
                lines.append("👍 Mes sólido. Buen trabajo.")
            else:
                lines.append("📊 Hay margen de mejora. Analiza qué te está frenando.")
            
            message = "\n".join(lines)
            
            await self.bot.send_message(
                chat_id=self.user_id,
                text=message,
                parse_mode=ParseMode.HTML
            )
            
            print(f"✅ Informe mensual enviado")
            
        except Exception as e:
            print(f"❌ Error al enviar informe mensual: {e}")
    
    def _calculate_weekly_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas de la última semana"""
        week_ago = date.today() - timedelta(days=7)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT status, COUNT(*) as count
            FROM tasks
            WHERE date(updated_at) >= ?
            AND parent_task_id IS NULL
            GROUP BY status
        """, (week_ago.strftime("%Y-%m-%d"),))
        
        results = cursor.fetchall()
        conn.close()
        
        stats = {'completed': 0, 'in_progress': 0, 'pending': 0}
        total = 0
        
        for row in results:
            stats[row['status']] = row['count']
            total += row['count']
        
        completion_rate = int((stats['completed'] / total * 100)) if total > 0 else 0
        
        return {
            'completed': stats['completed'],
            'in_progress': stats['in_progress'],
            'pending': stats['pending'],
            'completion_rate': completion_rate
        }
    
    def _calculate_monthly_stats(self) -> Dict[str, Any]:
        """Calcula estadísticas del último mes"""
        month_ago = date.today() - timedelta(days=30)
        
        conn = self.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM tasks
            WHERE status = 'completed'
            AND date(completed_at) >= ?
            AND parent_task_id IS NULL
        """, (month_ago.strftime("%Y-%m-%d"),))
        
        completed_tasks = cursor.fetchone()['count']
        
        cursor.execute("""
            SELECT COUNT(*) as count
            FROM projects
            WHERE status = 'completed'
            AND date(completed_at) >= ?
        """, (month_ago.strftime("%Y-%m-%d"),))
        
        completed_projects = cursor.fetchone()['count']
        
        conn.close()
        
        productivity_score = min(10, (completed_tasks // 3) + (completed_projects * 2))
        
        return {
            'completed': completed_tasks,
            'projects_completed': completed_projects,
            'productivity_score': productivity_score
        }