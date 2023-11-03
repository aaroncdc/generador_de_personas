"""
___________________________________________________________________________

            GENERACIÓN PROCEDURAL DE BASE DE DATOS DE PERSONAS
___________________________________________________________________________

Programa para generar datos de personas virtuales de manera procedural, para
realizar pruebas sobre bases de datos o placeholders.

NOTA: El programa genera datos de personas de forma aleatoria y no se corresponden
con la realidad, aunque es muy probable que algúnos de los nombres, números de
DNI y números de teléfono pudieran existir en la realidad, si bien dichos números
estarán asociados a alguna otra persona que no es la que se menciona en los datos
generados.

En el caso de que algún dato se corresponda con la realidad, es pura coincidencia
y el autor de éste programa no tiene constancia alguna de ello.

----------------------------------
ESTRUCTURAS DE LAS BASES DE DATOS
----------------------------------

La salida se puede guardar en formato CSV, JSON o SQLITE.

- CSV: Un único archivo. La primera fila contiene los nombres de los campos. A partir de
la segunda comienzan los datos.

- JSON: Contiene dos listas de datos:
    · campos: Lista de strings con los nombres de los campos
    · datos: Lista de diccionarios con los datos correspondientes a cada persona.

- SQLITE: Una base de datos con una única tabla. El nombre de la tabla corresponde
a la constante 'NOMBRE_TABLA', que por defecto es "personas". La tabla contiene
los datos de cada persona, en cada una de sus filas.

Los datos están organizados en los siguientes campos (o columnas):
- nombre: Nombre de la persona
- apellidos: Los apellidos de la persona
- calle: El nombre de la calle donde reside la persona
- numero: Número de portal/vivienda donde reside la persona
- cp: Código postal que le corresponde a la calle
- localidad: Ciudad de residencia
- provincia: Región o comunidad de residencia
- edad: Edad de la persona (a la fecha de introducción de los datos)
- sexo: Sexo de la persona (Hombre/Mujer)
- genero: Género de la persona (Hombre/Mujer/Transgénero)
- nacimiento: Fecha de nacimiento en formato yyyy-mm-dd
- dni: Número y letra del DNI
- telefono: Número de teléfono (sólo fijo)

----------------------------------
PARÁMETROS DE ENTRADA
----------------------------------

Los parámetros de entrada se encuentran abajo, organizados
en constantes que deben ser modificados antes de ejecutar
el programa.

----------------------------------
SALIDA
----------------------------------

El programa genera un archivo CSV, JSON o una base de datos
SQLITE con formato .db. El nombre será

PERSONAS_<localidad>_<año>.<extensión>

y su ubicación será la misma carpeta desde la cual se
ejecuta el programa.

----------------------------------
EJECUCIÓN
----------------------------------

Llamar al programa desde python. Ejemplo:

> python generarpoblacion.py

----------------------------------
ARCHIVOS DE DATOS CSV
----------------------------------

Las lístas de nombres están sacadas de

https://github.com/marcboquet/spanish-names

Que a su vez están extraidas de la base de datos del INE

http://www.ine.es/daco/daco42/nombyapel/nombyapel.htm

Las listas con los nombres de las calles de cada ciudad
se han extraido de OpenStreetMaps usando Overpass Turbo.

https://overpass-turbo.eu/

Ejemplo de query para la API de overpass:

[out:csv('addr:city','addr:housenumber','addr:postcode','addr:state','addr:street',building;true;',')][timeout:2500];
(
  nwr["addr:street"]({{bbox}});
);
out geom;

(Es necesario realizar una selección en el mapa con el area de la región)

O también

[out:csv('addr:city','addr:housenumber','addr:postcode','addr:state','addr:street',building;true;',')][timeout:2500];
{{geocodeArea:"<NOMBRE DE LA CIUDAD>"}}->.searchArea;
(
   nwr["addr:street"](area.searchArea);
);
out body;

para una ciudad en concreto.

"""
import random
import csv
import json
import sqlite3
import sys
from datetime import date

# MODIFICAR LOS SIGUIENTES PARÁMETROS DE FORMA ACORDE

LOC = "HENARES" # Localidad. ALCALA o HENARES (Incluye Madrid). Defecto: "HENARES"
ALLOW_EMPTY_POSTCODE = False # Se pueden escoger direcciones sin CP. Defecto: False
MALE_CHANCE = 65 # Probabilidad de que cada individuo sea hombre. Defecto: 65
TRANS_CHANCE = 1 # Probabilidad de que cada individuo sea transgénero. Defecto: 1
MIN_AGE = 24 # Edad mínima. Defecto: 24
MAX_AGE = 71 # Edad máxima. Defecto: 71
FECHA_ACTUAL = date(2024,1,1) # Edades y fechas de nacimiento relativas a esta fecha. Defecto: date(2024,1,1)
GENERAR = 1000 # Número de filas (personas) a generar. Defecto: 1000
FORMATO = "CSV" # Formato de salida. CSV, JSON o SQLITE. Defecto: "CSV"
NOMBRE_TABLA = "personas" # Nombre de la tabla con los datos (Sólo se usa para SQLITE). Defecto: "personas"

# Constantes con las rutas de los archivos de datos
CARPETA_CSV = "csv" # Nombre de la carpeta con los archivos CSV

"""
A continuación se incluye una estructura de datos con los datos de cada localidad.
El formato es:

"<Código de localidad>": ("<Nombre de la localidad>", 
"<Ruta del archivo CSV con la lista de calles y números>", "<prefijo telefónico>")

Se pueden añadir nuevas localidades de ésta forma, pero LOC debe estar definido
dentro de esta lista.
"""

ARCHIVOS_CSV = {
    "ALCALA": ("Alcalá de Henares", "alcaladh2.csv", "91"),
    "HENARES": ("Madrid", "chenares.csv", "91")
}

# Espacio para las variables, NO MODIFICAR
nhombre, nmujer, apellidos, calles, telefonos, dnis = [],[],[],[],[],[]

# -------------------- COMIENZO DEL PROGRAMA ----------------------------

# genFechaNacimiento (edad = 0, fecha_actual = date.today()), retorna date
def genFechaNacimiento(n: int = 0, curdate: date = date.today()) -> date:
    if n < MIN_AGE or n > MAX_AGE:
        edad = random.randint(MIN_AGE, MAX_AGE)
    else:
        edad = n
    hoy = curdate
    fechamin = date(hoy.year - edad, 1, 1)
    fechamax = date(hoy.year - edad, 12, 31)
    return fechamin + (fechamax - fechamin) * random.random()

# genTel(), retorna str con el número de teléfono
def genTel() -> str:
    numbers = []
    # Prefijo + (6,7 u 8) + 6 dígitos al azar
    return f"{ARCHIVOS_CSV[LOC][2]}{random.randint(6, 8)}{''.join([str(i) for i in random.sample(range(0, 9), 6)])}"

# gendni(), returna str con el número y letra de DNI
def gendni() -> str:
    # String con las letras del DNI, el orden importa
    LETRAS = "TRWAGMYFPDXBNJZSQVHLCKE"
    # El primer digito es siempre 0
    n1 = 0
    # El segundo dígito es 7,8 o 9 
    n2 = random.randint(7, 9)
    # El resto son elegidos al azar
    numbers = random.sample(range(0, 9), 6)
    # Convertir el número en un string
    dnistr = '' + str(n1) + str(n2) + ''.join([str(i) for i in numbers])
    # Se divide el número entre 23 y el resto es el índice que determina la letra.
    letra = LETRAS[int(dnistr)%23]
    return f"{dnistr}{letra}"

# genPersona(), retorna un diccionario con la estructura de datos de una persona
def genPersona() -> dict:
    # Determinar el sexo de la persona.
    sexo = "Hombre" if random.randint(0, 100) < MALE_CHANCE else "Mujer"
    nombre = ""
    papellidos = ""
    # Determinar el nombre de la persona, de acuerdo con su sexo
    if sexo == "Hombre":
        nombre = random.choice(nhombre)
    else:
        nombre = random.choice(nmujer)
    # Determinar los apellidos
    papellidos = f"{random.choice(apellidos)} {random.choice(apellidos)}"
    # Determinar la dirección
    direccion = random.choice(calles)
    # Determinar la edad
    edad = random.randint(MIN_AGE, MAX_AGE)
    # Generar un número de teléfono y DNI
    telefono = genTel()
    dni = gendni()
    # Comprobar que los números generados no estén ya en uso.
    # En caso contrario, generar uno nuevo que no esté en uso.
    while telefono in telefonos:
        telefono = genTel()
    while dni in dnis:
        dni = gendni()
    # Añadir los números a las listas de números en uso.
    telefonos.append(telefono)
    dnis.append(dni)
    # Devolver la estructura con los datos generados.
    return {
        "nombre": nombre,
        "apellidos": papellidos,
        "calle": ''.join(direccion[4].split(',')[0]).split(';')[0],
        "numero": ''.join(direccion[1].split(',')[0]).split(';')[0].split('-')[0],
        "cp": direccion[2],
        "localidad": direccion[0],
        "provincia": "Madrid",
        "edad": edad,
        "sexo": sexo,
        "genero": sexo if random.randint(0, 100) >= TRANS_CHANCE else "Transgénero",
        "nacimiento": genFechaNacimiento(edad, FECHA_ACTUAL).strftime("%Y-%m-%d"),
        "dni": dni,
        "telefono": telefono
    }

"""
---------- INICIO DEL PROGRAMA ----------
"""
if __name__ == "__main__":
    # Abrir la lista de nombres masculinos
    with open('nombres/hombres.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nhombre.append(row['nombre'])

    # Abrir la lista de nombres femeninos
    with open('nombres/mujeres.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            nmujer.append(row['nombre'])

    # Abrir la lista de apellidos
    with open('nombres/apellidos.csv', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            apellidos.append(row['apellido'])

    # CARGA DE DATOS
    if LOC in ARCHIVOS_CSV.keys():
        print(f"Abriendo {CARPETA_CSV}/{ARCHIVOS_CSV[LOC][1]} ...")
        try:
            with open(f'{CARPETA_CSV}/{ARCHIVOS_CSV[LOC][1]}', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    # Sólo se permiten CPs vacíos si se establece tál opción
                    if ALLOW_EMPTY_POSTCODE == False:
                        if row['addr:postcode'] == '':
                            continue
                    # No permitir números de portal/casa vacíos
                    if row['addr:housenumber'] == '':
                        continue
                    # Introducir los datos de la calle en la lista de calles
                    calles.append((row['addr:city'] if row['addr:city'] != "" else ARCHIVOS_CSV[LOC][0],
                                row['addr:housenumber'], row['addr:postcode'], 
                                row['addr:state'], row['addr:street']))
        except exc:
            print(f"ERROR: No se pudo abrir el archivo {CARPETA_CSV}/{ARCHIVOS_CSV[LOC][1]} para su lectura.\n{str(exc)}")    
    else:
        print(f"ERROR: La localidad {LOC} no está definida en ARCHIVOS_CSV.")
        sys.exit(1)


    # Si el formato de salida es CSV
    if FORMATO == "CSV":
        # Abrir el archivo CSV
        with open(f"PERSONAS_{LOC}_{FECHA_ACTUAL.strftime('%Y')}.csv", "w+", encoding="UTF-8") as csvfile:
            outp = csv.DictWriter(csvfile, genPersona().keys(), delimiter=',',lineterminator='\n')
            # Escribir una fila de cabecera con los nombres de los campos
            outp.writeheader()
            # Generar filas con los datos de cada persona e introducirlos en el archivo CSV
            for persona in range(0, GENERAR):
                outp.writerow(genPersona())
    # Si el formato de salida es JSON
    if FORMATO == "JSON":
        with open(f"PERSONAS_{LOC}_{FECHA_ACTUAL.strftime('%Y')}.json", "w+", encoding="UTF-8") as jsonfile:
            # No se usa json.dumps directamente, ésto es intencionado. Cada persona se genera en tiempo de ejecución.
            jsonfile.write('{\n') # Apertura del documento JSON
            jsonfile.write(f'"campos" : [\n') # Lista de strings con los nombres de los campos
            # Se genera una lista con los campos de la base de datos
            campos = [c for c in genPersona().keys()]
            for i in range(0, len(campos)):
                # Escribir el nombre del campo
                jsonfile.write("        \"" + campos[i] + "\"")
                # Si no es la última iteración, se escribe una coma para separar el elemento.
                jsonfile.write(",\n" if i < len(campos)-1 else "\n")
            # Se cierra la lista con los nombres de los campos, comienza la lista con los diccionarios de los datos
            jsonfile.write('    ],\n"datos": [\n')
            # Lista de cada persona
            for persona in range(0, GENERAR):
                # Se genera una nueva persona y se añade a la lista. Se añade una coma si no es la última iteración.
                jsonfile.write(json.dumps(genPersona(), ensure_ascii=False, indent=4) + (",\n" if persona < GENERAR -1 else "\n"))
            # Se cierra la lista y el documento. Fín.
            jsonfile.write('    ]\n}\n')
    # Si el formato de salida es SQLITE
    if FORMATO == "SQLITE":
        # Lista con los nombres de los campos
        campos = ', '.join([c for c in genPersona().keys()])
        # Se abre/crea la base de datos
        with sqlite3.connect(f"PERSONAS_{LOC}_{FECHA_ACTUAL.strftime('%Y')}.db") as con:
            cur = con.cursor()
            # Se crea la tabla de datos
            cur.execute("CREATE TABLE IF NOT EXISTS {}({})".format(NOMBRE_TABLA, campos))
            # Se introducen los datos de cada persona en la tabla. Los datos se generan en tiempo de ejecución.
            for persona in range(0, GENERAR):
                # Generar una nueva persona
                persona = genPersona()
                # Placeholders para los nombres de los campos ("?, ?, ?, ...")
                huecos = ', '.join('?' * len(persona.values()))
                # Consulta para insertar una nueva fila con los datos de la persona
                sql = 'INSERT INTO {} ({}) VALUES ({})'.format(NOMBRE_TABLA, campos,huecos)
                # Lista con los valores a introducir
                valores = [val for val in persona.values()]
                # Introducir los valores en la tabla
                cur.execute(sql, valores)