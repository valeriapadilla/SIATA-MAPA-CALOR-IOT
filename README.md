
# Calidad del Aire en Medellín - Docker Setup

Este proyecto visualiza la calidad del aire en Medellín a través de un dashboard interactivo. Utiliza datos en tiempo real de sensores para calcular el Índice de Calidad del Aire (AQI) basado en las concentraciones de PM2.5, y proporciona recomendaciones según el nivel de contaminación.

## Requisitos

- **Docker** debe estar instalado en tu sistema.

## Instalación y Ejecución con Docker

1. **Clonar este repositorio o descargar los archivos `app.py` y `Dockerfile`.**

2. **Construir la imagen Docker:**

   Navega hasta el directorio que contiene los archivos `Dockerfile` y `app.py`, y ejecuta el siguiente comando:

   ```bash
   docker build -t calidad-aire-medellin .
   ```

3. **Ejecutar el contenedor:**

   Una vez que la imagen Docker haya sido construida, ejecuta el siguiente comando para iniciar el contenedor:

   ```bash
   docker run -d -p 80:80 calidad-aire-medellin
   ```

4. **Acceder al Dashboard:**

   Abre tu navegador web y ve a la siguiente dirección para visualizar el dashboard interactivo:

   ```
   http://localhost:80
   ```

   Aquí podrás ver un mapa de calor que muestra la calidad del aire en Medellín junto con las recomendaciones basadas en los valores de AQI.

## Estructura del Proyecto

- `app.py`: Código fuente de la aplicación que obtiene datos de sensores, calcula el AQI, genera recomendaciones y visualiza la información en un mapa interactivo.
- `Dockerfile`: Configuración para construir la imagen Docker con todas las dependencias necesarias.

## Tecnologías Utilizadas

- **Python 3**: Lenguaje de programación principal.
- **Dash y Flask**: Frameworks para crear el servidor web y la interfaz de usuario.
- **Pandas y NumPy**: Librerías para el manejo y procesamiento de datos.
- **Plotly**: Utilizado para la visualización de datos en el mapa interactivo.
- **Docker**: Para contenerizar la aplicación y simplificar su despliegue.
