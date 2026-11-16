# Detección de Objetos en Tiempo Real (Django + OpenCV)

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-4.x%20%7C%205.x-092E20?logo=django&logoColor=white)
![OpenCV](https://img.shields.io/badge/OpenCV-DNN-5C3EE8?logo=opencv&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-14+-336791?logo=postgresql&logoColor=white)
![YOLOv8](https://img.shields.io/badge/YOLO-v8%20ONNX-FF6F00)

Aplicativo web desarrollado en Django que captura video en tiempo real desde la cámara web para detectar **mascarillas, cascos de seguridad y celulares** utilizando el módulo `cv2.dnn` de OpenCV con un modelo YOLOv8 en formato ONNX. El sistema superpone las detecciones en la transmisión en vivo y registra un historial persistente en PostgreSQL.

> ** Contexto Académico:** Construcción de Software (UNEMI)  
> ** Autores:** Abarca Diego, Gianmarcos Campoverde, Xavier Granizo

---

##  Funcionalidades Principales

* **Autenticación de Usuarios:** Sistema completo de registro e inicio de sesión para controlar el acceso al panel de monitoreo.
* **Detección en Tiempo Real:** Transmisión de video en vivo con renderizado de *bounding boxes*, etiquetas de clase y porcentaje de confianza.
* **Control Dinámico:** Conteo simultáneo de objetos detectados en pantalla y ajuste dinámico del umbral de confianza (*confidence threshold*).
* **Persistencia en Base de Datos:** Almacenamiento automático de los eventos detectados en PostgreSQL, incluyendo la captura fotográfica del momento.
* **Gestión de Historial:** Consulta de registros con filtros combinados por tipo de objeto y rango de fechas, paginación y exportación directa a formato **CSV**.

---

##  Requisitos Previos

Antes de comenzar, asegúrate de contar con:
* **Python** 3.10 o superior
* **PostgreSQL** 14 o superior
* **Cámara web** conectada y funcional en el equipo servidor
* **Git**

---

##  Instalación y Configuración

### 1. Clonar el repositorio y crear entorno virtual
```bash
git clone <URL_DEL_REPOSITORIO>
cd <NOMBRE_DE_LA_CARPETA>

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
# En Windows:
venv\Scripts\activate
# En Linux / macOS:
source venv/bin/activate
```

### 2. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 3. Configurar la base de datos y variables de entorno
1. Crea la base de datos en PostgreSQL ejecutando en tu cliente SQL o `psql`:
   ```sql
   CREATE DATABASE deteccion_db;
   ```
2. Copia el archivo de ejemplo de variables de entorno y configura tus credenciales de acceso:
   ```bash
   cp .env.example .env
   ```
   *(Asegúrate de completar los datos de conexión a PostgreSQL y la `SECRET_KEY` de Django dentro de `.env`).*

### 4. Configurar el modelo de IA
Coloca los archivos del modelo en la carpeta `modelos/` antes de iniciar el servidor (consulta la sección [Modelo de Detección](#-modelo-de-detección)).

### 5. Ejecutar migraciones e iniciar el servidor
```bash
python manage.py makemigrations deteccion
python manage.py migrate
python manage.py createsuperuser   # Opcional: crea un usuario administrador
python manage.py runserver
```
Abre tu navegador e ingresa a: **`http://127.0.0.1:8000/`**

---

##  Modelo de Detección

Por razones de tamaño y buenas prácticas, los archivos de pesos no se incluyen en el repositorio. El sistema requiere que ubiques manualmente dos archivos dentro de la carpeta `modelos/`:
* `modelos/modelo.onnx`
* `modelos/clases.txt` *(un nombre de clase por línea, respetando exactamente el orden del entrenamiento).*

### Consideraciones del Modelo:
* **Formato y dimensiones:** Debe ser un modelo **YOLOv8** exportado a ONNX con una resolución de entrada de `640x640`:
  ```bash
  yolo export model=best.pt format=onnx imgsz=640
  ```
* **Clases personalizadas:** El modelo estándar entrenado con COCO (`yolov8n`) reconoce celulares (`cell phone`), pero **no** detecta mascarillas ni cascos. Para detectar los tres elementos, debes utilizar pesos entrenados con datasets personalizados (por ejemplo, de *Roboflow* o *Kaggle*) que incluyan clases como `mask`, `helmet` o `hardhat`.
* **Mapeo de etiquetas:** Si tu modelo utiliza nombres de clase en inglés u otras variantes, puedes ajustar sus equivalencias al español en el diccionario `ALIAS` dentro de `deteccion/detector.py`.

---

##  Pruebas

Para ejecutar la batería de pruebas unitarias del proyecto:
```bash
python manage.py test
```

---

##  Estructura del Proyecto

```text
├── config/             # Configuración principal del proyecto Django (settings, urls, wsgi)
├── deteccion/          # Aplicación principal
│   ├── camara.py       # Captura y streaming de video con OpenCV
│   ├── detector.py     # Inferencia con cv2.dnn, procesamiento ONNX y mapeo de ALIAS
│   ├── models.py       # Modelos de base de datos para el historial de detecciones
│   └── views.py        # Lógica de vistas, filtros y exportación CSV
├── modelos/            # Directorio local para modelo.onnx y clases.txt (ignorado por Git)
├── templates/          # Plantillas HTML estilizadas con Bootstrap
├── .env.example        # Plantilla de variables de entorno
├── manage.py           # Utilidad de línea de comandos de Django
└── requirements.txt    # Dependencias del proyecto
```

---

##  Notas de Rendimiento y Uso

* **Ejecución de la cámara:** El flujo de video captura la cámara conectada físicamente al equipo donde se ejecuta `runserver` (pensado para uso local en laboratorio).
* **Optimización de FPS:** Si notas latencia o bajos fotogramas por segundo en equipos sin GPU dedicada, incrementa el valor de la variable `cada` dentro de `Camara.frames` en `deteccion/camara.py` (para procesar 1 de cada *N* fotogramas) o sube el umbral de confianza desde la interfaz web.
