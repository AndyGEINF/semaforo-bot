# SemáforoBot

SemáforoBot es un bot de trading diseñado para interactuar con diversas plataformas de intercambio utilizando la biblioteca CCXT. Este proyecto está estructurado para facilitar la gestión de señales de trading y el análisis de datos del mercado.

## Estructura del Proyecto

El proyecto está organizado de la siguiente manera:

```
semaforo-bot
├── src
│   ├── main.py                  # Punto de entrada de la aplicación.
│   ├── bot
│   │   ├── __init__.py          # Inicializa el paquete bot.
│   │   ├── semaforo_bot.py      # Contiene la clase SemaforoBot.
│   │   └── signal_analyzer.py   # Contiene la clase SignalAnalyzer.
│   ├── exchanges
│   │   ├── __init__.py          # Inicializa el paquete exchanges.
│   │   └── ccxt_client.py       # Contiene la clase CCXTClient.
│   ├── indicators
│   │   ├── __init__.py          # Inicializa el paquete indicators.
│   │   ├── technical_indicators.py # Funciones para indicadores técnicos.
│   │   └── market_metrics.py     # Funciones para métricas del mercado.
│   ├── api
│   │   ├── __init__.py          # Inicializa el paquete api.
│   │   ├── routes.py            # Define las rutas de la API.
│   │   └── models.py            # Modelos de datos para la API.
│   ├── database
│   │   ├── __init__.py          # Inicializa el paquete database.
│   │   └── redis_client.py       # Clase RedisClient para operaciones con Redis.
│   └── utils
│       ├── __init__.py          # Inicializa el paquete utils.
│       ├── config.py            # Gestión de configuración del proyecto.
│       └── logger.py            # Funciones para el registro de logs.
├── tests
│   ├── __init__.py              # Inicializa el paquete de pruebas.
│   ├── test_indicators.py       # Pruebas unitarias para indicadores.
│   └── test_bot.py              # Pruebas unitarias para SemaforoBot.
├── .env.example                  # Ejemplo de variables de entorno.
├── requirements.txt              # Lista de dependencias del proyecto.
├── README.md                     # Documentación del proyecto.
└── run.py                        # Ejecuta la aplicación.
```

## Instalación

Para instalar las dependencias del proyecto, asegúrate de tener Python 3.11 o superior y ejecuta el siguiente comando:

```
pip install -r requirements.txt
```

## Uso

Para ejecutar el bot, utiliza el siguiente comando:

```
python run.py
```

Asegúrate de configurar las variables de entorno necesarias en un archivo `.env` basado en el archivo `.env.example`.

## Contribuciones

Las contribuciones son bienvenidas. Si deseas contribuir, por favor abre un issue o un pull request en el repositorio.

## Licencia

Este proyecto está bajo la licencia MIT.