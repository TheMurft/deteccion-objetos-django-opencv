# Detección de objetos en tiempo real

Aplicación web desarrollada con **Django**, **OpenCV** y un modelo de detección de objetos tipo **YOLO exportado a ONNX**. El sistema utiliza la cámara web del computador, muestra las detecciones sobre el video y permite guardar un historial de detecciones.

## Autores

Reemplaza esta sección con los nombres reales de los integrantes del grupo:

- Nombre del estudiante 1

- Nombre del estudiante 2

## Funcionalidades

- Registro e inicio de sesión de usuarios.

- Captura de video desde la cámara web.

- Detección de objetos en tiempo real.

- Visualización de recuadros, etiquetas y nivel de confianza.

- Ajuste del umbral de confianza.

- Guardado de capturas y detecciones.

- Historial de detecciones con filtros por objeto y fecha.

- Paginación del historial.

- Exportación del historial a CSV.

## Tecnologías utilizadas

- Python 3.10 o superior.

- Django 5.

- OpenCV.

- NumPy.

- Pillow.

- SQLite o PostgreSQL.

- Modelo YOLO exportado al formato ONNX.

- Git y GitHub.

## Requisitos

Antes de instalar el proyecto, asegúrate de tener instalado:

- Python 3.10 o superior.

- PyCharm.

- Git.

- Una cámara web.

- PostgreSQL 14 o superior si vas a utilizar PostgreSQL.

> Para desarrollar y probar rápidamente, puedes utilizar SQLite. SQLite no necesita instalación porque viene incluido con Python y Django.

## Descargar el proyecto

Clona el repositorio desde la terminal de PyCharm:

```
git clone https://github.com/R0ddy21/deteccion-objetos-unemi.git
cd deteccion-objetos-unemi
```

Después abre en PyCharm la carpeta que contiene el archivo `manage.py`.

## Crear el entorno virtual en PyCharm

Desde la terminal integrada de PyCharm ejecuta:

```
py -3.10 -m venv .venv
```

Activa el entorno virtual en Windows:

```
.venv\Scripts\activate
```

En Linux o macOS utiliza:

```bash
source .venv/bin/activate
```

Si la activación fue correcta, la terminal mostrará `.venv` al inicio de la línea.

## Configurar el intérprete de Python en PyCharm

En PyCharm entra en:

```
File > Settings > Project > Python Interpreter
```

Selecciona el intérprete existente ubicado en:

```
.venv\Scripts\python.exe
```

En Windows, la ruta completa será parecida a:

```
C:\Users\TU_USUARIO\Documents\deteccion-objetos-unemi\.venv\Scripts\python.exe
```

## Instalar las dependencias

Con el entorno virtual activado, ejecuta:

```
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Para comprobar que Django está instalado:

```
python -m django --version
```

## Configurar la base de datos

### Opción A: SQLite, recomendada para comenzar

SQLite es la opción más sencilla para trabajar en PyCharm. No necesitas instalar PostgreSQL ni crear una base de datos manualmente.

Abre el archivo:

```
config/settings.py
```

Busca la configuración `DATABASES` y reemplázala por:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
```

Crea un archivo `.env` en la carpeta principal del proyecto:

```
SECRET_KEY=clave-secreta-para-desarrollo
DEBUG=True
```

Django creará automáticamente el archivo `db.sqlite3` cuando ejecutes las migraciones.

### Opción B: PostgreSQL

La guía de la práctica menciona PostgreSQL. Si el docente exige utilizarlo, crea una base de datos llamada:

```
deteccion_db
```

Puedes crearla desde pgAdmin o mediante SQL:

```sql
CREATE DATABASE deteccion_db;
```

Después crea el archivo `.env` en la carpeta principal del proyecto:

```
SECRET_KEY=clave-secreta-para-desarrollo
DEBUG=True
DB_NAME=deteccion_db
DB_USER=postgres
DB_PASSWORD=TU_CONTRASEÑA_DE_POSTGRES
DB_HOST=localhost
DB_PORT=5432
```

En `config/settings.py`, utiliza esta configuración:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.environ.get("DB_NAME", "deteccion_db"),
        "USER": os.environ.get("DB_USER", "postgres"),
        "PASSWORD": os.environ.get("DB_PASSWORD", ""),
        "HOST": os.environ.get("DB_HOST", "localhost"),
        "PORT": os.environ.get("DB_PORT", "5432"),
    }
}
```

Asegúrate de que el servicio de PostgreSQL esté iniciado.

## Aplicar las migraciones

Desde la terminal de PyCharm ejecuta:

```
python manage.py check
python manage.py makemigrations
python manage.py migrate
```

Para crear un usuario administrador:

```
python manage.py createsuperuser
```

## Configurar el modelo de detección

El código del proyecto no incluye un modelo YOLO listo para usar. El detector espera estos dos archivos:

```
modelos/
├── modelo.onnx
└── clases.txt
```

Abre `config/settings.py` y verifica que las rutas estén configuradas así:

```python
MODELO_ONNX = BASE_DIR / "modelos" / "modelo.onnx"
MODELO_CLASES = BASE_DIR / "modelos" / "clases.txt"
```

> No utilices una ruta fija como `C:\Modelos\modelo.onnx`, porque solo funcionará en un computador que tenga exactamente esa carpeta.

### Archivo `clases.txt`

`clases.txt` debe contener una clase por línea y en el mismo orden utilizado por el modelo. Por ejemplo:

```
person
hardhat
mask
cell phone
```

El contenido correcto depende del modelo que se haya utilizado para entrenar la detección.

### Modelo ONNX

El archivo `modelo.onnx` debe ser compatible con el detector de OpenCV y utilizar una entrada de 640 x 640 píxeles. Si tienes un modelo YOLO en formato `.pt`, puedes exportarlo con Ultralytics:

```
pip install ultralytics
 yolo export model=best.pt format=onnx imgsz=640
```

Después cambia el nombre del archivo exportado a `modelo.onnx` y cópialo dentro de la carpeta `modelos`.

Si no agregas el modelo, la aplicación puede iniciar, pero no realizará detecciones. La cámara mostrará un aviso indicando que falta `modelo.onnx`.

## Ejecutar la aplicación

Inicia el servidor con:

```
python manage.py runserver
```

Abre en el navegador:

```
http://127.0.0.1:8000/
```

La cámara se abrirá en el computador donde se está ejecutando el servidor Django. Cierra otras aplicaciones que estén usando la cámara, como Zoom, Teams o Google Meet.

Para detener el servidor presiona:

```
Ctrl + C
```

## Ejecutar las pruebas

```
python manage.py test
```

## Estructura del proyecto

```
deteccion-objetos-unemi/
├── config/                Configuración principal de Django
├── deteccion/             Aplicación de detección y modelos
├── modelos/               modelo.onnx y clases.txt
├── templates/             Plantillas HTML
├── media/                 Capturas guardadas por la aplicación
├── manage.py              Administrador de Django
├── requirements.txt       Dependencias del proyecto
├── .env                   Variables de entorno locales
└── db.sqlite3             Base SQLite, si se utiliza SQLite
```

## Solución de problemas

### `No module named django`

PyCharm está utilizando otro intérprete. Selecciona `.venv\Scripts\python.exe` en la configuración del proyecto y ejecuta:

```
pip install -r requirements.txt
```

### Error de conexión con PostgreSQL

Comprueba que PostgreSQL esté iniciado y que los datos de `.env` sean correctos, especialmente `DB_PASSWORD`, `DB_PORT` y `DB_NAME`.

### Falta `modelo.onnx`

Comprueba que existan estos archivos:

```
modelos\modelo.onnx
modelos\clases.txt
```

También revisa la configuración de `MODELO_ONNX` y `MODELO_CLASES` en `config/settings.py`.

### La cámara no funciona

Cierra otros programas que la estén utilizando y verifica los permisos de cámara de Windows. El proyecto intenta abrir la cámara predeterminada con el índice `0`.

### La cámara funciona, pero no hay detecciones

Comprueba que el modelo y `clases.txt` correspondan entre sí. También confirma que el modelo haya sido entrenado para reconocer los objetos esperados.

## Entrega de la práctica

Para la entrega se recomienda incluir:

- El enlace al repositorio de GitHub.

- El código fuente.

- `README.md`.

- `requirements.txt`.

- Una explicación de la instalación y ejecución.

- Un video demostrativo de máximo 3 minutos.

El video puede mostrar el proyecto en PyCharm, la ejecución del servidor, la cámara funcionando y las detecciones en la aplicación web.

## Seguridad

No subas al repositorio:

- El archivo `.env`.

- Contraseñas de PostgreSQL.

- Archivos privados.

- Bases de datos locales si contienen información real.

Agrega estas líneas al archivo `.gitignore`:

```
.env
.venv/
db.sqlite3
media/
__pycache__/
*.pyc
```
