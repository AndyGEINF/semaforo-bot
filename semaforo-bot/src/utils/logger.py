import logging
import sys

def setup_logger(name, level=logging.INFO):
    """Configura el logger para la aplicación."""
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    
    logger = logging.getLogger(name)
    logger.setLevel(level)
    logger.addHandler(handler)
    
    return logger

# Logger de la aplicación
app_logger = setup_logger('semaforo_bot')