

# blacklist

Una colección de diversas listas negras de hosts para usar en Pi-hole o software similar.

### Índice de listas
* [scam_hosts_srb.txt](/lists/scam_hosts_srb.txt) - Diversos sitios web de estafa, fraude, phishing y typosquatting dirigidos a usuarios de internet en Serbia (recolectados por miembros del foro de https://bezbedanbalkan.net/) - actualmente contiene 515 dominios exactos y únicos
* [crowdstrike_list.txt](/lists/crowdstrike_list.txt) - Lista que contiene dominios similares a Crowdstrike tras el error de BSOD de Crowdstrike Falcon
* [all.txt](/lists/all.txt) - Lista compilada de todas las demás listas

### Autores de la lista original utilizada para `scam_hosts_srb.txt`
* [@milos_rs_](https://twitter.com/milos_rs_ "@milos_rs_ on X")
* [maxxa](https://bezbedanbalkan.net/user-5.html "maxxa on Bezbedanbalkant.net")


--


### Ejemplos de uso para `build_list.py`

Uso de la herramienta:

```
usage: build_list.py [-h] [-s SECTION] [-f FILENAME] [-t TARGET] [--run] [--debug]

options:
  -h, --help            show this help message and exit
  -s SECTION, --section SECTION
                        Section name (eg: "Scam" or "typosquatting").
  -f FILENAME, --filename FILENAME
                        File with "raw" data. See raw.md for supported formats and substitutions.
  -t TARGET, --target TARGET
                        Target filename. If exists, it will be updated with the new content.
  --run                 Run the script. Otherwise just quit.
  --debug               Debug mode. Writes a lot.
```

El script `build_list.py` analizará cualquier archivo de texto con dominios en formato línea por línea y lo convertirá en un archivo de salida compatible con listas negras. El archivo de entrada debe cumplir los siguientes criterios:

* Cada línea debe ser un nuevo dominio.
* Cada dominio debe ser la primera palabra de la línea.

La herramienta aplicará las sustituciones de `subs.json` a cada línea que lea del archivo de entrada (por ejemplo, reemplazará `[.]` por `.`: puedes añadir las sustituciones que desees). No sobrescribirá el contenido antiguo; solo añadirá nuevos hosts en la sección correspondiente. La lista resultante de hosts contendrá hosts únicos en orden alfabético. La herramienta también escribirá encabezados de sección y algunas líneas de comentario debajo. La idea es ejecutar la herramienta para cada nuevo archivo de origen sin procesar para poblar diferentes secciones del archivo de salida resultante. La lista negra de este repositorio se ha creado utilizando esta herramienta, por lo que puedes consultar [scam_hosts_srb.txt](/lists/scam_hosts_srb.txt) para ver un ejemplo de salida.

#### Ejemplos de uso:

El siguiente ejemplo leerá `scam.txt` para obtener nuevos hosts, abrirá `out.txt`, buscará la sección existente llamada `Scam` y añadirá los nuevos hosts.
```
./build_list.py -f scam.txt -s Scam -t out.txt --run
```

# Pruebas Unitarias para build_list.py

## Resumen

Pruebas unitarias exhaustivas para el script de gestión de listas negras `build_list.py`. El conjunto de pruebas incluye 36 tests que cubren todas las funciones principales y casos extremos.

## Cobertura de Pruebas

### Clases de Prueba

1. **TestParseLine** (6 tests)
   - Análisis de dominios simples
   - Manejo de valores separados por espacios
   - Aplicación de sustituciones (individual y múltiple)
   - Eliminación de espacios en blanco
   - Manejo de cadenas vacías

2. **TestLoadSubs** (6 tests)
   - Carga de JSON válido
   - Verificación del mecanismo de caché
   - Manejo de errores de archivo no encontrado
   - Manejo de errores de JSON inválido
   - Manejo de errores de E/S

3. **TestLoadNewData** (5 tests)
   - Carga de archivo válido
   - Filtrado de líneas vacías
   - Manejo de errores de archivo no encontrado
   - Manejo de errores de E/S
   - Análisis de valores separados por espacios

4. **TestParseTarget** (6 tests)
   - Análisis de una sola sección
   - Análisis de múltiples secciones
   - Manejo de comentarios
   - Advertencia por contenido fuera de secciones
   - Manejo de secciones malformadas
   - Manejo de archivos vacíos

5. **TestWriteData** (4 tests)
   - Escritura en una sola sección
   - Escritura en múltiples secciones
   - Adición automática de saltos de línea
   - Verificación de codificación UTF-8

6. **TestConfigureLogging** (2 tests)
   - Configuración de nivel INFO
   - Configuración de nivel DEBUG

7. **TestIntegration** (3 tests)
   - Flujo de trabajo completo (cargar → analizar → fusionar → escribir)
   - Creación de nueva sección
   - Manejo de sustituciones vacías

8. **TestEdgeCases** (7 tests)
   - Múltiples espacios consecutivos
   - Líneas con solo espacios en blanco
   - Secciones consecutivas sin espaciado
   - Secciones vacías
   - Caracteres especiales en dominios

## Ejecución de las Pruebas

### Ejecutar todas las pruebas:
```bash
cd ~/<repo location>/blacklist/scripts
python -m unittest test_build_list -v
```

### Ejecutar una clase de prueba específica:
```bash
python -m unittest test_build_list.TestParseLine -v
```

### Ejecutar una prueba específica:
```bash
python -m unittest test_build_list.TestParseLine.test_parse_line_simple -v
```

### Ejecutar con cobertura (si coverage.py está instalado):
```bash
pip install coverage
coverage run -m unittest test_build_list
coverage report -m
coverage html  # Generates HTML report in htmlcov/
```

## Resultados de las Pruebas

```
----------------------------------------------------------------------
Ran 36 tests in 0.018s

OK
```

## Características Principales Probadas

✅ **Operaciones de Archivos**
- Lectura de archivos con codificación adecuada (UTF-8)
- Escritura de archivos con codificación adecuada
- Manejo de errores para archivos perdidos o corruptos

✅ **Análisis de Datos**
- Extracción de dominios de varios formatos
- Sustituciones de cadenas con caché
- Análisis de estructura de archivos basada en secciones
- Conservación de comentarios

✅ **Manejo de Errores**
- FileNotFoundError
- IOError
- json.JSONDecodeError
- IndexError/ValueError

✅ **Casos Extremos**
- Archivos y secciones vacíos
- Entrada malformada
- Contenido fuera de secciones
- Caracteres especiales
- Múltiples escenarios de espacios en blanco

✅ **Rendimiento**
- Caché de sustituciones para evitar E/S de archivos repetida
- Comprensiones de listas eficientes

## Dependencias de las Pruebas

- Python 3.6+ (utiliza f-strings)
- `unittest` (biblioteca estándar)
- `unittest.mock` (biblioteca estándar)
- `tempfile` (biblioteca estándar)

## Integración Continua

Estas pruebas pueden integrarse en pipelines de CI/CD:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: python -m unittest discover -s scripts -p 'test_*.py' -v
```

## Mejoras Futuras

- [ ] Añadir benchmarks de rendimiento
- [ ] Añadir pruebas de mutación
- [ ] Probar la función main() con análisis completo de argumentos
- [ ] Añadir pruebas basadas en propiedades con hypothesis
- [ ] Probar escenarios de acceso concurrente a archivos
