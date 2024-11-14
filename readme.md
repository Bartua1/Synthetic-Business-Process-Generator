# Generador de Procesos Sintéticos

Módulo de Python que genera procesos de negocio sintéticos y sus correspondientes registros de eventos. El generador crea hasta 2.500 procesos únicos con nombres de actividades realistas, asignación de recursos y datos de ejecución.

## Características

- Genera modelos de proceso con complejidad configurable
- Crea nombres de actividades realistas mediante integración con LLM
- Produce registros de eventos con atributos detallados de casos y actividades
- Soporta generación de procesos en múltiples hilos
- Visualiza flujos de proceso utilizando GraphViz
- Genera datos realistas de departamentos y recursos
- Incluye horarios laborales y reglas de negocio configurables

## Instalación

### Requisitos previos

- Python 3.8+
- GraphViz (para visualización de procesos)
- LMStudio (para nombrado inteligente de actividades)

```bash
# Instalar paquetes Python necesarios
pip install -r requirements.txt

# Instalar GraphViz
# Para Ubuntu/Debian:
sudo apt-get install graphviz

# Para macOS:
brew install graphviz

# Para Windows:
# Descargar e instalar desde: https://graphviz.org/download/
```

## Estructura del Proyecto

```
.
├── generator.py              # Script principal de ejecución
├── data_gen/                # Módulos principales de generación
│   ├── __init__.py         # Inicialización del paquete
│   ├── LMStudioConnector.py    # Integración con API de LMStudio
│   ├── NameGenerator.py        # Generación de nombres de proceso
│   ├── ProcessGenerator.py     # Generación de flujos de proceso
│   └── ProcessDataGenerator.py # Generación de registros de eventos
├── data/                    # Registros de eventos generados
└── images/                  # Visualizaciones de procesos generadas
```

## Uso

1. Iniciar el servidor LMStudio (necesario para el nombrado inteligente de actividades)

2. Ejecutar el generador:
```bash
python generator.py
```

### Configuración

El generador se puede configurar mediante los siguientes parámetros en `generator.py`:

```python
main(num_threads=10)  # Número de hilos paralelos de generación
```

Parámetros de generación de procesos en `ProcessGenerator`:
```python
ProcessGenerator(
    min_nodes=5,           # Número mínimo de actividades
    max_nodes=10,          # Número máximo de actividades
    min_connections=1,     # Conexiones salientes mínimas por actividad
    max_connections=3,     # Conexiones salientes máximas por actividad
    process_name="Ejemplo" # Nombre del proceso para contexto
)
```

Parámetros de generación de registros en `ProcessDataGenerator`:
```python
ProcessDataGenerator(
    num_cases=500,        # Número de instancias de proceso
    start_date=...,       # Fecha de inicio para el registro
    end_date=...         # Fecha de fin para el registro
)
```

## Archivos Generados

### Visualizaciones de Proceso (`images/`)
- `{nombre_proceso}.png`: Visualización GraphViz del flujo del proceso
- Muestra actividades, conexiones y dirección del flujo
- Utiliza código de colores para nodos de inicio/fin y actividades

### Registros de Eventos (`data/`)
- `{nombre_proceso}.csv`: Datos del registro de eventos generado con las siguientes columnas:
  - `case_id`: Identificador único para cada instancia de proceso
  - `activity`: Nombre de la actividad
  - `timestamp`: Hora de inicio de la actividad
  - `complete_timestamp`: Hora de finalización de la actividad
  - `customer_id`: Identificador sintético del cliente
  - `priority`: Prioridad del caso (Baja/Media/Alta)
  - `channel`: Canal de comunicación
  - `department`: Departamento responsable
  - `product_category`: Tipo de producto/servicio
  - `value`: Valor monetario del caso
  - `resource`: Recurso asignado
  - `duration_minutes`: Duración de la actividad
  - `cost`: Coste de la actividad
  - `status`: Estado de la actividad
  - `system`: Sistema utilizado
  - `automated`: Indicador de automatización

## Reglas de Generación de Procesos

- Cada proceso tiene un nodo INICIO y FIN
- Todas las actividades deben ser alcanzables desde INICIO
- El nodo FIN debe ser alcanzable desde todas las actividades
- No se permiten conexiones directas de INICIO a FIN
- Las actividades tienen al menos una conexión entrante y una saliente
- Horario laboral: 9:00 a 18:00, de lunes a viernes

## Contribuir

¡Las contribuciones son bienvenidas! No dudes en enviar una Pull Request.

## Licencia

Este proyecto está licenciado bajo la Licencia MIT - consulta el archivo LICENSE para más detalles.

## Agradecimientos

- Desarrollado con Python y GraphViz
- Utiliza LMStudio para el nombrado inteligente de procesos
- Inspirado en el modelado de procesos de negocio del mundo real

