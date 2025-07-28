import pandas as pd
import numpy as np
import sys # Para salir del script de forma controlada
import os # Para manejar rutas y directorios

def cargar_datos(ruta_archivo, columnas_esperadas):
    """
    Carga un archivo CSV en un DataFrame de Pandas.
    Maneja errores si el archivo no se encuentra o hay problemas de lectura.
    Valida si el archivo contiene las columnas esperadas.
    """
    try:
        df = pd.read_csv(ruta_archivo)
        print(f"Archivo '{ruta_archivo}' cargado exitosamente.")
        
        # Identificar y mostrar los nombres de las columnas cargadas
        columnas_cargadas = df.columns.tolist()
        print("\n--- Columnas identificadas en el archivo cargado ---")
        for col in columnas_cargadas:
            print(f"- {col}")

        # Validar si todas las columnas esperadas están presentes
        columnas_faltantes = [col for col in columnas_esperadas if col not in columnas_cargadas]
        if columnas_faltantes:
            print("\n Error: El archivo cargado no contiene todas las columnas esperadas.")
            print(f"Columnas faltantes: {', '.join(columnas_faltantes)}")
            return None # Retorna None si faltan columnas
        else:
            print("\n Todas las columnas esperadas están presentes en el archivo.")

        print("\n--- Vista previa del DataFrame original ---")
        print(df.head())
        print("\n--- Información del DataFrame original ---")
        df.info()
        print("\n--- Valores nulos iniciales ---")
        print(df.isnull().sum())
        return df
    except FileNotFoundError:
        print(f" Error: El archivo '{ruta_archivo}' no se encontró.")
        print("Por favor, asegúrate de que el nombre y la ruta sean correctos.")
        return None
    except pd.errors.EmptyDataError:
        print(f" Error: El archivo '{ruta_archivo}' está vacío.")
        return None
    except pd.errors.ParserError:
        print(f" Error: Problema al parsear el archivo '{ruta_archivo}'. Verifica el formato.")
        return None
    except Exception as e:
        print(f" Ocurrió un error inesperado al intentar leer el archivo CSV: {e}")
        return None

def limpiar_y_transformar_datos(df):
    """
    Aplica una serie de técnicas de limpieza y transformación al DataFrame.
    """
    print("\n" + "="*60)
    print("INICIANDO PROCESO DE LIMPIEZA Y TRANSFORMACIÓN DE DATOS")
    print("="*60)

    # 1. Manejo de Valores Nulos
    print("\n--- Paso 1: Manejo de Valores Nulos ---")
    
    # Identificar la última fecha para rellenar nulos en fechas
    ultima_fecha_registro = None
    if 'Fecha_Registro' in df.columns:
        # Asegurarse de que la columna sea de tipo datetime primero
        df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'], errors='coerce')
        if not df['Fecha_Registro'].isnull().all(): # Si no todos son nulos
            ultima_fecha_registro = df['Fecha_Registro'].max()
            print(f"  Última fecha registrada identificada para nulos de fecha: {ultima_fecha_registro}")
        else:
            print("   La columna 'Fecha_Registro' no contiene ninguna fecha válida para inferir la última.")
    
    for columna in df.columns:
        if df[columna].isnull().any():
            if pd.api.types.is_numeric_dtype(df[columna]):
                # Rellenar datos numéricos nulos con la media
                media_col = df[columna].mean()
                df[columna].fillna(media_col, inplace=True)
                print(f"   Columna '{columna}': Nulos numéricos rellenados con la media ({media_col:.2f}).")
            elif pd.api.types.is_datetime64_any_dtype(df[columna]):
                # Rellenar datos tipo fecha con la última fecha registrada
                if ultima_fecha_registro is not None:
                    df[columna].fillna(ultima_fecha_registro, inplace=True)
                    print(f"   Columna '{columna}': Nulos de fecha rellenados con la última fecha registrada ({ultima_fecha_registro.strftime('%Y-%m-%d')}).")
                else:
                    # Si no hay última fecha válida, rellenar con una fecha por defecto o el valor más frecuente.
                    # Aquí usaremos el valor más frecuente como alternativa si no hay una última fecha clara.
                    if not df[columna].mode().empty:
                        df[columna].fillna(df[columna].mode()[0], inplace=True)
                        print(f"   Columna '{columna}': Nulos de fecha rellenados con la fecha más frecuente (sin una última fecha clara).")
                    else:
                        df[columna].fillna(pd.to_datetime('1900-01-01'), inplace=True) # Valor predeterminado
                        print(f"   Columna '{columna}': Nulos de fecha rellenados con '1900-01-01' (sin fechas válidas).")
            else:
                # Rellenar datos tipo texto con "Desconocido"
                df[columna].fillna('Desconocido', inplace=True)
                print(f"   Columna '{columna}': Nulos de texto rellenados con 'Desconocido'.")

    print("\nValores nulos después de rellenar:")
    print(df.isnull().sum())

    # 2. Conversión de Tipos de Datos
    print("\n--- Paso 2: Conversión de Tipos de Datos ---")
    
    # Asegurar que Fecha_Registro sea datetime
    if 'Fecha_Registro' in df.columns:
        df['Fecha_Registro'] = pd.to_datetime(df['Fecha_Registro'], errors='coerce')
        # Esto ya se manejó en el paso 1 si quedaron NaT
        print("   Columna 'Fecha_Registro': Asegurada como tipo datetime.")

    # Convertir 'Edad' a int (si ya no tiene nulos y es numérico)
    if 'Edad' in df.columns and pd.api.types.is_numeric_dtype(df['Edad']) and df['Edad'].isnull().sum() == 0:
        df['Edad'] = df['Edad'].astype(int)
        print("   Columna 'Edad': Convertida a tipo entero (int).")
    else:
        print("   Columna 'Edad': No se pudo convertir a int (posibles nulos o tipo incorrecto).")

    # Asegurar 'Valor_Total_Compras' como numérico
    if 'Valor_Total_Compras' in df.columns:
        df['Valor_Total_Compras'] = pd.to_numeric(df['Valor_Total_Compras'], errors='coerce')
        # Si la coerción creó nulos (ej. texto no numérico), se rellenarán con la media
        if df['Valor_Total_Compras'].isnull().any():
            df['Valor_Total_Compras'].fillna(df['Valor_Total_Compras'].mean(), inplace=True)
            print("   Algunos valores de 'Valor_Total_Compras' no eran numéricos y fueron rellenados con la media.")
        print("   Columna 'Valor_Total_Compras': Asegurada como tipo numérico (float).")

    # Mapear 'Tiene_Descuento_Activo' a booleano
    if 'Tiene_Descuento_Activo' in df.columns:
        # Primero, asegurar que los valores sean strings para .lower()
        df['Tiene_Descuento_Activo'] = df['Tiene_Descuento_Activo'].astype(str).str.lower().str.strip()
        mapeo_descuento = {'si': True, 'no': False, 'true': True, 'false': False}
        df['Tiene_Descuento_Activo'] = df['Tiene_Descuento_Activo'].map(mapeo_descuento).fillna(False) # Rellenar con False si hay valores inesperados
        print("   Columna 'Tiene_Descuento_Activo': Mapeada a tipo booleano.")

    # Asegurar que otras columnas numéricas sean float o Int64
    for col in ['Numero_Visitas_Web_Ultimos_30_Dias', 'Promedio_Articulos_Por_Compra']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            if df[col].isnull().any():
                df[col].fillna(df[col].median(), inplace=True)
                print(f"  ⚠️ Columna '{col}': Algunos valores no eran numéricos y fueron rellenados con la mediana.")
            if df[col].dtype == 'float64' and df[col].apply(float.is_integer).all():
                df[col] = df[col].astype('Int64') # Int64 para enteros que pueden tener nulos
            print(f"   Columna '{col}': Asegurada como tipo numérico.")

    # 3. Eliminación de Duplicados
    print("\n--- Paso 3: Eliminación de Duplicados ---")
    filas_duplicadas = df.duplicated().sum()
    if filas_duplicadas > 0:
        df.drop_duplicates(inplace=True)
        print(f"   Se eliminaron {filas_duplicadas} filas duplicadas.")
    else:
        print("   No se encontraron filas duplicadas.")

    # 4. Normalización y Estandarización de Datos Categóricos
    print("\n--- Paso 4: Normalización de Datos Categóricos ---")
    columnas_categoricas = ['Ciudad', 'Genero', 'Tipo_Producto_Preferido', 'Metodo_Pago_Preferido']
    for col in columnas_categoricas:
        if col in df.columns:
            # Asegurarse de que sea string antes de lower/strip para evitar errores con nulos/otros tipos
            df[col] = df[col].astype(str).str.lower().str.strip()
            print(f"   Columna '{col}': Convertida a minúsculas y sin espacios.")

    # Mapeo de valores inconsistentes (ejemplo para Ciudad) - MEJORA: Identificar automáticamente
    print("\n--- Mapeo de valores inconsistentes (Ciudades, Géneros, etc.) ---")
    
    # Generar un mapeo para Ciudad
    if 'Ciudad' in df.columns:
        print(f"Valores únicos en 'Ciudad' ANTES de mapeo: {df['Ciudad'].unique()}")
        
        # Aquí puedes definir un mapeo más robusto si tienes muchos casos.
        # Por simplicidad, se puede pedir al usuario o definir uno común.
        # EJEMPLO: Estandarización manual de algunas ciudades conocidas
        mapeo_ciudades = {
            'méxico df': 'ciudad de mexico',
            'cdmx': 'ciudad de mexico',
            'guadalajara, jal.': 'guadalajara',
            'monterrey, n.l.': 'monterrey',
            'gdl': 'guadalajara',
            'mty': 'monterrey',
            'puebla de zaragoza': 'puebla'
        }
        df['Ciudad'] = df['Ciudad'].replace(mapeo_ciudades)
        print("   Columna 'Ciudad': Mapeo de inconsistencias aplicado (ejemplos comunes).")
        print(f"Valores únicos en 'Ciudad' DESPUÉS de mapeo: {df['Ciudad'].unique()}")
    else:
        print("  ℹ Columna 'Ciudad' no encontrada para mapeo.")

    # Puedes extender esto para otras columnas categóricas si tienen inconsistencias:
    if 'Genero' in df.columns:
        print(f"\nValores únicos en 'Genero' ANTES de mapeo: {df['Genero'].unique()}")
        mapeo_genero = {
            'm': 'masculino',
            'f': 'femenino',
            'male': 'masculino',
            'female': 'femenino'
        }
        df['Genero'] = df['Genero'].replace(mapeo_genero)
        print("   Columna 'Genero': Mapeo de inconsistencias aplicado.")
        print(f"Valores únicos en 'Genero' DESPUÉS de mapeo: {df['Genero'].unique()}")
    else:
        print("  ℹ Columna 'Genero' no encontrada para mapeo.")

    if 'Tipo_Producto_Preferido' in df.columns:
        print(f"\nValores únicos en 'Tipo_Producto_Preferido' ANTES de mapeo: {df['Tipo_Producto_Preferido'].unique()}")
        # Ejemplo: Normalizar "electronicos" y "electrodomesticos"
        mapeo_productos = {
            'electronicos': 'electrónica',
            'electrodomesticos': 'electrodomésticos',
            'electro': 'electrónica'
        }
        df['Tipo_Producto_Preferido'] = df['Tipo_Producto_Preferido'].replace(mapeo_productos)
        print("   Columna 'Tipo_Producto_Preferido': Mapeo de inconsistencias aplicado.")
        print(f"Valores únicos en 'Tipo_Producto_Preferido' DESPUÉS de mapeo: {df['Tipo_Producto_Preferido'].unique()}")
    else:
        print("  ℹ Columna 'Tipo_Producto_Preferido' no encontrada para mapeo.")

    # 5. Creación de Nuevas Características (Feature Engineering)
    print("\n--- Paso 5: Creación de Nuevas Características ---")
    if 'Edad' in df.columns:
        bins = [0, 18, 30, 50, np.inf]
        labels = ['Joven', 'Adulto Joven', 'Adulto', 'Senior']
        df['Rango_Edad'] = pd.cut(df['Edad'], bins=bins, labels=labels, right=False, include_lowest=True)
        print("   Nueva columna 'Rango_Edad' creada.")

    if 'Fecha_Registro' in df.columns and pd.api.types.is_datetime64_any_dtype(df['Fecha_Registro']):
        df['Ano_Registro'] = df['Fecha_Registro'].dt.year
        df['Mes_Registro'] = df['Fecha_Registro'].dt.month
        # Asegurarse de que 'locale' esté disponible para nombres de días en español
        try:
            df['Dia_Semana_Registro'] = df['Fecha_Registro'].dt.day_name(locale='es_MX')
        except AttributeError: # Si 'es_MX' no está disponible en el sistema
            df['Dia_Semana_Registro'] = df['Fecha_Registro'].dt.day_name() # Por defecto en inglés
            print("  ⚠️ No se pudo usar 'es_MX' para el día de la semana. Usando configuración regional por defecto.")
        print("   Nuevas columnas de tiempo ('Ano_Registro', 'Mes_Registro', 'Dia_Semana_Registro') creadas.")

    # Asegurarse de que 'Valor_Total_Compras' y 'Promedio_Articulos_Por_Compra' existen antes de operar
    if 'Valor_Total_Compras' in df.columns and 'Promedio_Articulos_Por_Compra' in df.columns:
        # Aquí se usa Promedio_Articulos_Por_Compra para calcular Valor_Promedio_Por_Articulo.
        # Si la idea era Valor_Promedio_Por_Compra, se necesitaría una columna de "Número_de_Compras" o "Transacciones".
        # Basado en el script original, parece que 'Frecuencia_Compras' es la candidata para 'Valor_Promedio_Por_Compra'
        if 'Frecuencia_Compras' in df.columns:
            # Rellenar cualquier NaN/0 en 'Frecuencia_Compras' antes de la división para evitar errores
            df['Frecuencia_Compras'] = pd.to_numeric(df['Frecuencia_Compras'], errors='coerce').fillna(1).astype(int)
            df['Valor_Promedio_Por_Compra'] = df['Valor_Total_Compras'] / df['Frecuencia_Compras']
            df['Valor_Promedio_Por_Compra'].replace([np.inf, -np.inf], np.nan, inplace=True) # Manejar divisiones por cero si 'Frecuencia_Compras' era 0
            df['Valor_Promedio_Por_Compra'].fillna(df['Valor_Promedio_Por_Compra'].mean(), inplace=True) # Rellenar nulos resultantes
            print("   Nueva columna 'Valor_Promedio_Por_Compra' creada.")
        else:
            print("   No se pudo crear 'Valor_Promedio_Por_Compra': Columna 'Frecuencia_Compras' no encontrada.")
    else:
        print("   No se pudo crear 'Valor_Promedio_Por_Compra': Columnas necesarias no encontradas.")

    # 6. Renombrar Columnas (Opcional)
    print("\n--- Paso 6: Renombrar Columnas ---")
    # Es importante que el mapeo aquí coincida con las columnas finales esperadas.
    # Aquí estamos renombrando las columnas a snake_case en minúsculas.
    column_mapping = {
        'ID_Cliente': 'id_cliente',
        'Nombre_Cliente': 'nombre_cliente',
        'Fecha_Registro': 'fecha_registro',
        'Edad': 'edad',
        'Valor_Total_Compras': 'valor_total_compras',
        'Tiene_Descuento_Activo': 'tiene_descuento_activo',
        'Ciudad': 'ciudad',
        'Genero': 'genero',
        'Tipo_Producto_Preferido': 'tipo_producto_preferido',
        'Metodo_Pago_Preferido': 'metodo_pago_preferido',
        'Numero_Visitas_Web_Ultimos_30_Dias': 'numero_visitas_web_ultimos_30_dias',
        'Promedio_Articulos_Por_Compra': 'promedio_articulos_por_compra'
        # Añade aquí cualquier otra columna que necesites renombrar si existiera en el CSV original
        # 'Frecuencia_Compras': 'frecuencia_compras', # Si existiera esta columna
        # 'Ultima_Compra_Dias': 'ultima_compra_dias', # Si existiera esta columna
    }
    
    # Solo renombra las columnas que realmente existen en el DataFrame y están en nuestro mapeo
    df.rename(columns={k: v for k, v in column_mapping.items() if k in df.columns}, inplace=True)
    print("   Columnas renombradas a minúsculas y formato snake_case (solo las presentes en el mapeo).")


    print("\n" + "="*60)
    print("PROCESO DE LIMPIEZA Y TRANSFORMACIÓN FINALIZADO")
    print("="*60)

    print("\n--- Vista previa del DataFrame LIMPIO y TRANSFORMADO ---")
    print(df.head())
    print("\n--- Información del DataFrame LIMPIO y TRANSFORMADO ---")
    df.info()
    print("\n--- Valores nulos FINALES ---")
    print(df.isnull().sum())

    return df

# --- Bloque principal del script ---
if __name__ == "__main__":
    # --- Configuración de salida ---
    # Define el directorio donde se guardarán todos los archivos generados.
    output_dir = "archivos_clientes_limpios"
    os.makedirs(output_dir, exist_ok=True) # Crea el directorio si no existe.
    print(f"\n Los archivos de salida se guardarán en el directorio: '{output_dir}'")
    # --- Fin Configuración de salida ---

    # Columnas esperadas en el archivo de entrada
    columnas_requeridas = [
        "Fecha_Registro", "Edad", "Valor_Total_Compras", "Tiene_Descuento_Activo",
        "Ciudad", "Genero", "Tipo_Producto_Preferido", "Metodo_Pago_Preferido",
        "Nombre_Cliente", "Numero_Visitas_Web_Ultimos_30_Dias",
        "Promedio_Articulos_Por_Compra", "ID_Cliente"
    ]

    print("\n¡Bienvenido al script de limpieza de datos de clientes!")
    print("Por favor, introduce la ruta completa y el nombre del archivo CSV a limpiar.")
    print("Ejemplo: C:\\Usuarios\\TuUsuario\\Documentos\\clientes_2023.csv")
    
    ruta_input = input("Ruta y nombre del archivo CSV: ").strip()

    # 1. Cargar los datos
    df_clientes = cargar_datos(ruta_input, columnas_requeridas)

    if df_clientes is not None:
        # 2. Limpiar y transformar los datos
        # Usamos .copy() para no modificar el DataFrame original si lo necesitáramos más adelante
        df_clientes_limpio = limpiar_y_transformar_datos(df_clientes.copy())

        # Opción para el usuario: Continuar al siguiente paso o finalizar
        print("\n" + "#"*60)
        print("¿Deseas guardar el DataFrame limpio o finalizar el script?")
        print("Escribe 'guardar' para guardar o cualquier otra cosa para salir.")
        decision = input("Tu elección: ").lower().strip()
        print("#"*60 + "\n")

        if decision == 'guardar':
            # Definir el nombre del archivo de salida
            nombre_base_entrada = os.path.splitext(os.path.basename(ruta_input))[0]
            nombre_archivo_salida = f"{nombre_base_entrada}_limpio.csv"
            ruta_archivo_salida = os.path.join(output_dir, nombre_archivo_salida)

            try:
                df_clientes_limpio.to_csv(ruta_archivo_salida, index=False, encoding='utf-8')
                print(f" DataFrame limpio guardado exitosamente en: '{ruta_archivo_salida}'")
                print("¡El script ha finalizado exitosamente!")
            except Exception as e:
                print(f" Error al guardar el archivo: {e}")
                print("¡El script ha finalizado con errores al guardar!")
        else:
            print("Saliendo del script sin guardar el archivo limpio. ¡Hasta luego!")
            sys.exit() # Sale del programa
    else:
        print("Debido a errores en la carga de datos, el script no puede continuar. Saliendo.")
        sys.exit() # Sale del programa si la carga falló