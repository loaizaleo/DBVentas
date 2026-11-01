# DBVentas

Base de datos **MySQL** para registrar los modelos de tenis, sus colores y las ventas diarias, junto con las herramientas en Python que generan los datos que se cargan en ella.

## Objetivo

Centralizar en una base de datos relacional (esquema `referencias`) la información de:

- **Marcas** (Nike, Adidas, Puma, ...).
- **Modelos** de cada marca y sus **colores** (principal, secundario, terciario y código hexadecimal).
- **Ventas**: qué modelo se vendió, cuántas unidades y en qué fecha.

Con esto se pueden responder preguntas como *¿cuál es el modelo más vendido?*, *¿cuánto se vendió un día?* o *¿qué modelos tienen el blanco como color principal?*

## Lenguaje y tecnologías

- **SQL (MySQL 8)** para el modelo de datos y las consultas.
- **Python 3** con **Tkinter**, **Pillow** y **NumPy** para las herramientas de apoyo.

## Archivos

| Archivo | Descripción |
|---|---|
| `sql.txt` | Script con la creación de tablas, migraciones, inserciones y consultas de ejemplo. |
| `clasificador_V2.py` | Ordena fotos de productos en carpetas por referencia (igual al de [reconocimiento](https://github.com/loaizaleo/reconocimiento)). |
| `registradorV3.py` | Registra ventas a partir de fotos en `ventas_log.csv` (igual al de reconocimiento). |
| `inspector_colorV4.py` | Abre una imagen y, al hacer clic, muestra el color en RGB y HEX para copiarlo. Sirve para llenar la tabla `color_hex`. |
| `categorias_codigoV2.txt` | Referencias de modelos con el formato `<modelos_id>_<marcas_id>_<modelo>_<colores>`. |
| `marcas.txt` | Tabla de códigos de marca. |
| `base/ventas_log*.csv` | Ventas registradas (`fecha,cantidad,modelos_id`), listas para importar a la tabla `ventas`. |

## Modelo de datos

```
marcas (marcas_id, nombre_marca)
   │ 1
   │
   ▼ N
modelos (modelos_id, marcas_id, modelo_ref)
   │ 1
   ├──────────────► N colores_modelo (color_modelo_id, modelo_id, color_nombre, orden_color)
   ├──────────────► N color_hex      (color_hex_id, modelos_id, color_1, color_2, color_3)
   └──────────────► N ventas         (ventas_id, fecha, cantidad, modelos_id)
```

`orden_color` puede ser `principal`, `secundario` o `terciario`.

## Uso

### 1. Crear la base de datos

En MySQL Workbench (o la consola de MySQL):

```sql
CREATE DATABASE referencias;
USE referencias;
```

Luego ejecute el bloque **QUERY 1** de `sql.txt` (las sentencias `CREATE TABLE`).

> `sql.txt` es un archivo de trabajo: además de crear tablas incluye borrados (`DROP`, `DELETE`) y ejemplos. **No lo ejecute completo de una sola vez**; seleccione y ejecute solo el bloque que necesite.

### 2. Generar datos

```bash
pip install pillow numpy
python registradorV3.py      # registra ventas en ventas_log.csv
python inspector_colorV4.py  # obtiene colores HEX de una foto
```

### 3. Importar ventas

Copie el CSV a la carpeta de carga de MySQL (`C:/ProgramData/MySQL/MySQL Server 8.0/Uploads/`) y use `LOAD DATA INFILE`, como en el ejemplo de `sql.txt`.

### Consultas útiles (incluidas en `sql.txt`)

- Modelos de una marca y cuántos tiene.
- Colores de cada modelo.
- Total vendido en una fecha (`SUM(cantidad)`).
- Modelo más vendido (`GROUP BY modelos_id ORDER BY ... DESC`).
- Unir modelos, ventas y colores con `INNER JOIN`.

## Notas

- Al final de `sql.txt` hay un `INSERT INTO ventas` incompleto (le falta el `modelos_id`); es una plantilla, no se ejecuta tal cual.
- La ruta de `LOAD DATA INFILE` es la de MySQL en Windows; cámbiela si usa otro sistema.
