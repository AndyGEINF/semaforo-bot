# Este archivo es el punto de entrada de la aplicación. Se encarga de iniciar el bot y ejecutar la lógica principal.

from fastapi import FastAPI
from bot.semaforo_bot import SemaforoBot
from utils.config import load_config

def main():
    # Cargar la configuración
    config = load_config()
    
    # Inicializar el bot
    bot = SemaforoBot(config)
    
    # Iniciar el bot
    bot.start()

if __name__ == "__main__":
    main()