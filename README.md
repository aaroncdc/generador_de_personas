# Generador de personas
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
