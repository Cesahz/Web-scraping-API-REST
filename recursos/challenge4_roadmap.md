# 🗺️ Roadmap para dominar el Challenge 4
## 2 semanas — orden lógico de aprendizaje

---

## La regla general

> Cada capa depende de la anterior. No saltees niveles.
> Si algo no te sale solo, lo estudiás. Si te sale solo, pasás.

---

## 📅 Semana 1 — Fundamentos que sostienen todo

### Día 1-2 — Python esencial para el challenge
**Prioridad: ALTA**

Lo que tenés que dominar sin dudar:

- Diccionarios: crear, acceder, `.get()`, iterar
- Listas de tuplas: `[(a, b), (c, d)]` — es el formato que usa psycopg2
- List comprehensions: `[x for x in lista if condicion]`
- Funciones con `try/except`
- `f-strings` y `.strip()`, `.replace()`

**Cómo practicarlo:**
Agarrá la celda 4 (scraping de libros) y reescribila desde cero sin mirar.
Si podés hacer eso, el Python del challenge está dominado.

**No necesitás:**
- Clases, herencia, decoradores
- Nada de async/await
- Ningún framework

---

### Día 2-3 — requests + BeautifulSoup
**Prioridad: ALTA**

Lo que tenés que dominar:

```
requests
├── .get(url, params={}, timeout=10)
├── .raise_for_status()
└── .json()

BeautifulSoup
├── .find("etiqueta", class_="clase")
├── .find_all("etiqueta")
├── .text + .strip()
└── ["atributo"]  → para href, class, title
```

**Cómo practicarlo:**
Elegí cualquier sitio web simple (no dinámico con JavaScript).
Abrí el inspector del navegador (F12), encontrá una etiqueta, extraela con BS4.
Repetí 3-4 veces con elementos distintos del mismo sitio.

**Señal de que lo dominaste:**
Podés scrapear Books to Scrape de memoria, sin documentación.

---

### Día 3-4 — psycopg2 y PostgreSQL desde Python
**Prioridad: ALTA**

Lo que tenés que dominar:

```
Conexión:
conn = psycopg2.connect(...)
cur = conn.cursor()

Lectura:
cur.execute("SELECT ...")
cur.fetchall()   → lista de tuplas
cur.fetchone()   → una tupla o None

Escritura:
cur.execute("INSERT ...", (val1, val2))
execute_values(cur, "INSERT ...", lista_de_tuplas)
conn.commit()    → siempre al final

Patrón RETURNING:
cur.execute("INSERT ... RETURNING id")
id = cur.fetchone()[0]
```

**Cómo practicarlo:**
Creá una DB de prueba con una tabla simple (nombre, edad).
Insertá 10 filas desde Python, leelas, filtralas. Sin mirar el código del challenge.

**No necesitás:**
- SQLAlchemy (es un bonus, no obligatorio)
- ORM ni modelos

---

### Día 4-5 — Consumo de APIs con requests
**Prioridad: MEDIA-ALTA**

Lo que tenés que dominar:

```
El ciclo completo:
1. Leer la documentación de la API
2. Probar en Thunder Client / Postman
3. Entender la estructura del JSON que devuelve
4. Escribir la función en Python que navega ese JSON
5. Manejar errores (404, timeout, campo ausente)
```

Navegación de JSON anidado:
```python
data["docs"][0]["author_name"][0]   # lista dentro de dict dentro de dict
data.get("birth_date", "")          # valor default si no existe
```

**Cómo practicarlo:**
Abrí Thunder Client. Hacé requests a Open Library manualmente.
Anotá en un bloc qué devuelve cada endpoint.
Después replicalo en Python sin mirar el código del challenge.

**Señal de que lo dominaste:**
Podés consultar Open Library y extraer nombre + birth_year + works de un autor
sin mirar el código previo.

---

### Día 5-6 — SQL en PostgreSQL (DBeaver)
**Prioridad: MUY ALTA** — es lo que más se evalúa

#### Nivel 1 — Base (ya lo tenés)
```sql
SELECT, FROM, WHERE, ORDER BY, LIMIT
BETWEEN, IS NULL, IS NOT NULL
LIKE, DISTINCT
```

#### Nivel 2 — Lo que viene en el challenge
```sql
-- JOIN simple
SELECT b.title, c.name
FROM books b
JOIN categories c ON c.id = b.category_id;

-- JOIN en cadena (N:M)
FROM books b
JOIN book_author ba ON ba.book_id = b.id
JOIN authors a ON a.id = ba.author_id;

-- Agregaciones
COUNT(*), AVG(), ROUND(), SUM()

-- GROUP BY + HAVING
GROUP BY columna
HAVING COUNT(*) >= 5   -- filtra grupos, no filas

-- UPDATE y DELETE seguros
UPDATE tabla SET col = val WHERE condicion;
DELETE FROM tabla WHERE condicion;
```

#### Nivel 3 — Para defender el challenge con autoridad
```sql
-- EXPLAIN ANALYZE
EXPLAIN ANALYZE SELECT ...;

-- Índices
CREATE INDEX idx_nombre ON tabla(columna);

-- INSERT con RETURNING
INSERT INTO tabla (...) VALUES (...) RETURNING id;

-- ON CONFLICT
ON CONFLICT DO NOTHING
ON CONFLICT (columna) DO NOTHING
```

**Cómo practicarlo:**
Las 5 consultas del challenge, reescribirlas desde cero en DBeaver.
Luego inventar variaciones: "los 3 peores", "categorías con más de 20 libros", etc.

---

## 📅 Semana 2 — Integración y defensa

### Día 7-8 — Rehacé el challenge completo desde cero
**Prioridad: CRÍTICA**

Sin mirar el código anterior. Solo con:
- La documentación de este roadmap
- DBeaver abierto
- Thunder Client para probar la API

El objetivo no es que salga perfecto. Es encontrar qué partes
te traban para saber qué repasar.

**Orden de reconstrucción:**
1. Crear las 4 tablas con DDL (sin mirar)
2. Celda 1: imports + conexión
3. Celda 2-3: scraping de categorías + inserción
4. Celda 4-5: scraping de libros + inserción
5. Celda 6-7: función Open Library
6. Celda 8: pipeline de autores
7. Las 5 consultas en DBeaver

---

### Día 9-10 — Pulir los puntos débiles
Lo que te trabó al rehacer → dedicarle un día entero.
Típicamente es alguno de estos tres:
- La paginación del scraping
- El manejo del cache + RETURNING en psycopg2
- Los JOINs en cadena con GROUP BY

---

### Día 11-12 — Preparar la defensa oral
**Prioridad: ALTA**

Preguntas que te pueden hacer y que tenés que poder responder sin dudar:

```
¿Por qué usaste ON CONFLICT DO NOTHING?
¿Qué pasa si no hacés commit?
¿Por qué el 54% de autores dio NULL?
¿Qué es el cache y por qué lo implementaste?
¿Qué diferencia hay entre WHERE y HAVING?
¿Por qué la tabla book_author tiene PK compuesta?
¿Qué hace RETURNING id?
¿Por qué el índice mejora la performance?
¿Qué es un Sequential Scan vs Index Scan?
¿Por qué usaste Open Library y no otra API?
```

Respondelas en voz alta. Si tartamudeás → repasás ese concepto.

---

### Día 13-14 — Simulacro completo
Cerrás todo. Abrís Jupyter, DBeaver, Thunder Client.
Rehacés el challenge como si fuera la evaluación real.
Cronometrado. Sin ayuda.

---

## 🎯 Prioridades absolutas (si te quedara poco tiempo)

```
1. SQL — JOINs en cadena + GROUP BY + HAVING    ████████████  imprescindible
2. psycopg2 — INSERT + RETURNING + commit       ███████████   imprescindible
3. BeautifulSoup — find/find_all + paginación   ██████████    muy importante
4. API Open Library — función completa          █████████     importante
5. Índices + EXPLAIN ANALYZE                    ███████       importante para defender
6. Cache en memoria                             █████         bonus, fácil de explicar
```

---

## 📚 Recursos por tecnología

| Tecnología | Recurso recomendado |
|------------|---------------------|
| BeautifulSoup | Documentación oficial: `crummy.com/software/BeautifulSoup/bs4/doc/` |
| requests | `docs.python-requests.org` — solo la sección Quickstart |
| psycopg2 | `psycopg.org/docs/usage.html` — sección Basic module usage |
| PostgreSQL SQL | `postgresql.org/docs/current/tutorial.html` |
| Open Library API | `openlibrary.org/developers/api` |
| Thunder Client | Extensión de VSCode, sin documentación necesaria — jugás directo |

---

## ⚡ La regla de oro para la evaluación

> Si lo podés rehacer solo en 2 horas, lo dominaste.
> Si necesitás más de 4 horas, hay algo que repasar.
> El objetivo no es memorizarlo. Es entender cada decisión.
