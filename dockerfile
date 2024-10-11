# Usar una imagen base de Ubuntu 22.04
FROM ubuntu:22.04

# Actualizar e instalar Python y pip
RUN apt update && apt install -y python3 python3-pip

# Instalar las dependencias necesarias
RUN pip3 install dash flask requests pandas numpy plotly scipy

# Establecer el directorio de trabajo dentro del contenedor
WORKDIR /parcial3

# Copiar el archivo app.py al contenedor
COPY app.py .

# Exponer el puerto 80
EXPOSE 80

# Comando para ejecutar la aplicación
CMD ["python3", "app.py"]
