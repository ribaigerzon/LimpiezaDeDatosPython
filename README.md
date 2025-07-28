# LimpiezaDeDatosPython
Script en Python para el proceso de limpieza de datos

Este repositorio contiene un script de Python diseñado para transformar tus datos de clientes a partir de un archivo CSV, pasándolos de un estado "desordenado" a un formato limpio, consistente y listo para análisis. Olvídate de la tediosa limpieza manual; este script automatiza el proceso, ahorrándote tiempo y garantizando la calidad de tus datos.

¿Para qué sirve?
Imagina tener un historial de ventas con datos de clientes con información incompleta, nombres de ciudades escritos de mil formas diferentes, o valores numéricos que no son lo que parecen. Este script actúa como tu asistente personal de limpieza de datos, realizando las siguientes tareas clave:

Identificación y Corrección de Errores:

- Manejo Inteligente de Nulos: Rellena automáticamente los datos faltantes. Para valores numéricos, usa la media de la columna; para texto, inserta "Desconocido"; y para fechas, utiliza la última fecha registrada para asegurar coherencia.

- Estandarización de Formatos: Convierte texto a minúsculas, elimina espacios extra, y asegura que las fechas y números tengan el formato correcto.

Organización y Consistencia:

- Eliminación de Duplicados: Identifica y remueve filas repetidas para evitar sesgos en tu análisis.

- Unificación de Nombres: Corrige inconsistencias en datos categóricos (ej. "CDMX", "México DF" se unifican a "ciudad de mexico" para evitar errores de interpretación).

Preparación para el Análisis:

Creación de Nuevas Características (Feature Engineering): Genera columnas adicionales útiles para análisis, como Rango_Edad (Joven, Adulto, Senior) o extracciones de tiempo (Año_Registro, Mes_Registro).

En resumen, este script transforma tus datos "sucios" en información "limpia" y utilizable, dejándolos listos para ser consumidos por herramientas como Power BI, Excel o cualquier plataforma de análisis de datos.

¿Cómo funciona?
El script te guiará paso a paso a través del proceso:

Solicitud de Archivo: Al ejecutarlo, te pedirá la ruta completa y el nombre del archivo CSV de clientes que deseas limpiar.

Carga y Validación: Intentará cargar el archivo y te mostrará un listado de las columnas detectadas. Verificará que tu CSV contenga las columnas esperadas (como "Fecha_Registro", "Edad", "Ciudad", etc.) y te informará si falta alguna para asegurar la integridad del proceso.

Proceso de Limpieza: Ejecutará automáticamente las rutinas de limpieza y transformación descritas anteriormente, informándote de cada paso.

Guardado del Resultado: Una vez finalizada la limpieza, te preguntará si deseas guardar el DataFrame resultante. Si confirmas, generará un nuevo archivo CSV limpio dentro de una carpeta dedicada (archivos_clientes_limpios) para mantener tu espacio de trabajo ordenado. El nuevo archivo tendrá un nombre que indicará que ha sido procesado (ej. nombre_original_limpio.csv).
