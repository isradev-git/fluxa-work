"""
Sistema de logging para el bot de productividad
Este archivo configura los logs para rastrear errores y eventos
"""
import logging
from datetime import datetime
import os

# Crear carpeta de logs si no existe
if not os.path.exists('logs'):
    os.makedirs('logs')

# EXPLICACIÓN: Configuramos diferentes niveles de log
# DEBUG: información detallada para diagnóstico (todo lo que pasa)
# INFO: confirmaciones de que las cosas funcionan
# WARNING: advertencias de algo que podría ser un problema
# ERROR: errores que impiden que algo funcione
# CRITICAL: errores graves que pueden detener el bot

def setup_logger(name):
    """
    Crea un logger personalizado para un módulo específico
    
    Args:
        name: Nombre del módulo (ej: 'tasks', 'projects', 'main')
    
    Returns:
        logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Capturamos TODO (debug y superiores)
    
    # Evitar duplicar handlers si ya existen
    if logger.handlers:
        return logger
    
    # HANDLER 1: Archivo con TODOS los logs (debug y superiores)
    # Este archivo tendrá información muy detallada
    file_handler = logging.FileHandler(
        f'logs/{name}.log',
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    
    # HANDLER 2: Archivo solo con ERRORES (error y critical)
    # Este archivo solo guardará los problemas importantes
    error_handler = logging.FileHandler(
        f'logs/{name}_errors.log',
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    
    # HANDLER 3: Consola (lo que vemos al ejecutar el bot)
    # Mostramos INFO y superiores para no saturar la consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # FORMATO del log: [FECHA HORA] NIVEL - MÓDULO - MENSAJE
    # Ejemplo: [2024-10-30 15:30:45] INFO - tasks - Usuario hizo clic en tarea ID 5
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)s - %(name)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Aplicar formato a todos los handlers
    file_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    logger.addHandler(console_handler)
    
    return logger


# DECORADOR para logging automático de funciones
# EXPLICACIÓN: Un decorador es una función que "envuelve" otra función
# para añadirle funcionalidad extra (en este caso, logging automático)
def log_function_call(logger):
    """
    Decorador que registra automáticamente cuando se llama una función
    y si tiene errores
    
    Uso:
        @log_function_call(logger)
        async def mi_funcion(update, context):
            # código aquí
    """
    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Extraer el nombre de la función
            func_name = func.__name__
            
            # LOG cuando SE INICIA la función
            logger.info(f"🔵 INICIO: {func_name}()")
            
            try:
                # EJECUTAR la función original
                result = await func(*args, **kwargs)
                
                # LOG cuando TERMINA CORRECTAMENTE
                logger.info(f"✅ FIN: {func_name}() - Éxito")
                return result
                
            except Exception as e:
                # LOG cuando HAY UN ERROR
                logger.error(
                    f"❌ ERROR en {func_name}(): {type(e).__name__}: {str(e)}",
                    exc_info=True  # Esto añade el stack trace completo
                )
                # Volver a lanzar el error para no ocultarlo
                raise
        
        return wrapper
    return decorator


# Logger general del bot
bot_logger = setup_logger('bot')

# EXPLICACIÓN de cómo usar este sistema:
# 
# 1. En cada archivo de handlers, importa:
#    from logger_config import setup_logger, log_function_call
#
# 2. Crea un logger para ese módulo:
#    logger = setup_logger('tasks')  # o 'projects', 'notes', etc.
#
# 3. Usa el decorador en funciones async importantes:
#    @log_function_call(logger)
#    async def view_task(update, context):
#        # tu código aquí
#
# 4. Añade logs manuales donde necesites:
#    logger.debug("Variable x vale: " + str(x))
#    logger.info("Usuario completó la tarea")
#    logger.warning("La tarea no tiene proyecto asociado")
#    logger.error("No se pudo guardar en la base de datos")
#
# Los logs se guardarán en:
# - logs/tasks.log (TODO)
# - logs/tasks_errors.log (solo ERRORES)
# - Consola (INFO y superiores)