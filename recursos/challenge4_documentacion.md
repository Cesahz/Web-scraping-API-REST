# 📚 Challenge 4 — Books Scraping Pipeline
## Documentación completa del flujo de trabajo

---

## 🗺️ Visión general del pipeline

```
Books to Scrape (sitio web)
        │
        │  BeautifulSoup + requests
        ▼
┌─────────────────────┐
│  Scraping           │  → categorías + libros + URLs
└─────────────────────┘
        │
        │  Por cada libro → URL de detalle
        ▼
┌─────────────────────┐
│  Open Library API   │  → nombre, birth_year, country, external_id, obras
└─────────────────────┘
        │
        │  psycopg2
        ▼
┌─────────────────────┐
│  PostgreSQL         │  → categories, books, authors, book_author
└─────────────────────┘
        │
        ▼
   Consultas SQL
```

---

## 🗄️ Modelo de base de datos

### Tablas y relaciones

```
categories          books                    authors
──────────          ──────                   ───────
id (PK)      ←─FK─ id (PK)                  id (PK)
name                title                    name
                    price                    birth_year
                    rating                   country
                    category_id              external_api_id (UNIQUE)
                    url                      total_known_works
                    created_at               api_source
                                             created_at
                         │                       │
                         └──────┐   ┌────────────┘
                                ▼   ▼
                            book_author
                            ───────────
                            book_id (FK → books)
                            author_id (FK → authors)
                            PK compuesta (book_id, author_id)
```

### Relaciones
- `books` → `categories`: muchos a uno (N:1). Un libro tiene una categoría.
- `books` ↔ `authors`: muchos a muchos (N:M) a través de `book_author`.

### Constraints importantes
- `books.price`: `CHECK (price >= 0)`
- `books.rating`: `CHECK (rating >= 1 AND rating <= 5)`
- `authors.external_api_id`: `UNIQUE` → evita duplicar el mismo autor de la API
- `book_author`: `PRIMARY KEY (book_id, author_id)` → evita relaciones duplicadas
- FKs con `ON DELETE CASCADE` en `book_author`

---

## 🐍 Celda 1 — Imports y conexión

```python
import requests
from bs4 import BeautifulSoup
import psycopg2
from psycopg2.extras import execute_values
import time

conn = psycopg2.connect(
    host="localhost",
    port=5432,
    dbname="books_pipeline",
    user="postgres",
    password="postgres"
)
cur = conn.cursor()
```

### ¿Qué hace cada librería?
| Librería | Rol |
|----------|-----|
| `requests` | Descarga páginas web y hace llamadas HTTP a APIs |
| `BeautifulSoup` | Navega y extrae datos del HTML descargado |
| `psycopg2` | Conecta Python con PostgreSQL |
| `execute_values` | Inserción masiva eficiente (bulk insert) |
| `time` | Para `sleep()` y respetar rate limits |

### Conceptos clave
- `conn` = el canal abierto con la DB (el teléfono)
- `cur` = el cursor que ejecuta SQL (la voz que habla)
- Toda escritura en PostgreSQL requiere `conn.commit()` para confirmarse

---

## 🕷️ Celda 2 — Scraping de categorías

```python
BASE_URL = "https://books.toscrape.com/"

response = requests.get(BASE_URL)
soup = BeautifulSoup(response.text, "html.parser")

sidebar = soup.find("ul", class_="nav nav-list")
category_links = sidebar.find_all("li")[1:]  # [0] es "Books" (el padre)

categories = []
for li in category_links:
    a = li.find("a")
    name = a.text.strip()
    url  = BASE_URL + a["href"]
    categories.append((name, url))
```

### ¿Cómo funciona BeautifulSoup?
El HTML es un árbol de etiquetas. BS4 te permite navegarlo:
- `.find("etiqueta", class_="clase")` → primer elemento que coincide
- `.find_all("etiqueta")` → todos los elementos como lista
- `.text` → el texto dentro de la etiqueta
- `["atributo"]` → accede a un atributo HTML (como `href`, `class`)
- `.strip()` → elimina espacios y saltos de línea del texto

### Resultado
Lista de tuplas: `[("Travel", "https://..."), ("Mystery", "https://..."), ...]`
~50 categorías encontradas.

---

## 💾 Celda 3 — Insertar categorías

```python
execute_values(
    cur,
    "INSERT INTO categories (name) VALUES %s ON CONFLICT DO NOTHING",
    [(cat[0],) for cat in categories]
)
conn.commit()
```

### Conceptos clave
- `execute_values` → inserta todas las filas de una sola vez (más eficiente que un loop)
- `ON CONFLICT DO NOTHING` → si la categoría ya existe, no rompe ni duplica
- `conn.commit()` → confirma la escritura en la DB

---

## 📖 Celda 4 — Scraping de libros

```python
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}

def scrape_books_from_category(category_name, category_url):
    books = []
    url = category_url

    while url:  # recorre todas las páginas
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        articles = soup.find_all("article", class_="product_pod")

        for article in articles:
            title = article.h3.a["title"]
            price_text = article.find("p", class_="price_color").text
            price = float(price_text.replace("£", "").replace("Â", "").strip())
            rating_class = article.find("p", class_="star-rating")["class"][1]
            rating = RATING_MAP.get(rating_class, 0)
            relative_url = article.h3.a["href"].replace("../../../", "catalogue/")
            book_url = BASE_URL + relative_url
            books.append({"title": title, "price": price,
                          "rating": rating, "category": category_name, "url": book_url})

        next_btn = soup.find("li", class_="next")
        if next_btn:
            next_href = next_btn.find("a")["href"]
            url = url.rsplit("/", 1)[0] + "/" + next_href
        else:
            url = None

        time.sleep(0.3)
    return books
```

### Lógica de paginación
```
Entrar a categoría
    └── ¿Hay botón "next"? → SÍ → construir URL siguiente → repetir
                          → NO → salir del while
```

### Extracción de datos por libro
| Dato | Dónde está en el HTML | Cómo se extrae |
|------|-----------------------|----------------|
| Título | `<h3><a title="...">` | `article.h3.a["title"]` |
| Precio | `<p class="price_color">` | `.text` + limpiar `£` |
| Rating | `<p class="star-rating One/Two/...">` | `["class"][1]` → `RATING_MAP` |
| URL | `<h3><a href="...">` | `["href"]` + reemplazar ruta relativa |

### Resultado
~1000 libros scrapeados de ~50 categorías.

---

## 💾 Celda 5 — Insertar libros

```python
for category_name, books in all_books:
    category_id = cat_db[category_name]
    rows = [(b["title"], b["price"], b["rating"], category_id, b["url"]) for b in books]
    execute_values(cur, """
        INSERT INTO books (title, price, rating, category_id, url)
        VALUES %s ON CONFLICT DO NOTHING
    """, rows)
conn.commit()
```

### Conceptos clave
- `cat_db` es un diccionario `{"Travel": 3, "Mystery": 7, ...}` creado con un SELECT previo
- Se usa para resolver el `category_id` (FK) antes de insertar
- Un solo `commit()` al final es más eficiente que uno por categoría

---

## 🔍 Celda 6 — Intentar extraer autor del HTML

```python
def get_author_from_book_page(book_url):
    try:
        response = requests.get(book_url, timeout=10)
        soup = BeautifulSoup(response.text, "html.parser")
        rows = soup.find("table", class_="table table-striped")
        if rows:
            for tr in rows.find_all("tr"):
                th = tr.find("th")
                td = tr.find("td")
                if th and "author" in th.text.lower():
                    return td.text.strip()
        return None  # Books to Scrape no expone el autor → usar API
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return None
```

### Resultado
Siempre devuelve `None` porque Books to Scrape no tiene el campo autor en el HTML.
Por eso la API es obligatoria.

---

## 🌐 Celda 7 — Consultar Open Library API

### Flujo de la función

```
get_author_from_openlibrary(title)
        │
        ├── GET /search.json?title={titulo}&limit=1
        │       └── Extraer author_name y author_key
        │
        ├── ¿author_key en cache? → SÍ → devolver cache (sin nueva llamada HTTP)
        │                         → NO → continuar
        │
        ├── GET /authors/{author_key}.json
        │       └── Extraer birth_date, location
        │
        ├── GET /authors/{author_key}/works.json?limit=0
        │       └── Extraer size (cantidad de obras)
        │
        └── Guardar en cache y devolver dict
```

### Estructura del dict que devuelve

```python
{
    "name": "George Orwell",
    "birth_year": 1903,
    "country": "England",          # NULL en ~99% de los casos
    "external_api_id": "OL12345A", # ID interno de Open Library
    "total_known_works": 42,
    "api_source": "open_library"
}
```

### Manejo de errores
| Caso | Comportamiento |
|------|---------------|
| Libro no encontrado | Devuelve dict con NULLs y `api_source: "open_library"` |
| Timeout | Devuelve dict con NULLs y `api_source: "open_library_error"` |
| Error HTTP (404, 500) | `raise_for_status()` → capturado por except |
| Autor ya consultado | Cache devuelve resultado sin nueva llamada HTTP |

### Por qué el cache importa
Sin cache: 1000 libros × 3 requests = 3000 llamadas HTTP
Con cache: si 50 libros comparten autor → 50 × 3 = 150 llamadas ahorradas

---

## 💾 Celda 8 — Pipeline completo autores → DB

### Lógica de inserción (el caso más complejo del proyecto)

```
Por cada libro:
    │
    ├── Consultar API → author_data (dict)
    │
    ├── INSERT INTO authors ... ON CONFLICT (external_api_id) DO NOTHING
    │       RETURNING id
    │           │
    │           ├── RETURNING devuelve id → autor nuevo, usar ese id
    │           │
    │           └── RETURNING devuelve None → autor ya existía
    │                   └── SELECT id WHERE external_api_id = ...
    │
    ├── ¿Sigue siendo None? → autor "Unknown" sin external_api_id
    │       └── SELECT por nombre → si no existe → INSERT sin UNIQUE
    │
    └── INSERT INTO book_author (book_id, author_id)
            ON CONFLICT DO NOTHING
```

### Por qué `RETURNING id`
En vez de INSERT + SELECT por separado, PostgreSQL devuelve el id generado
directamente en el mismo INSERT. Más eficiente y atómico.

### Resultado
- ~952 autores únicos insertados
- ~1000 relaciones en `book_author`
- 54.8% de autores no encontrados en la API (dato real de Open Library)

---

## 📊 Consultas SQL del challenge

### Consulta 1 — Libros baratos y bien rankeados
```sql
SELECT b.title, b.price, b.rating, c.name AS category
FROM books b
JOIN categories c ON c.id = b.category_id
WHERE b.rating > 3 AND b.price < 10
ORDER BY b.rating DESC, b.price ASC;
```
**Conceptos:** JOIN simple, WHERE con AND, ORDER BY múltiple.

---

### Consulta 2 — Autor con peor promedio de rating (mín. 5 libros)
```sql
SELECT a.name,
       ROUND(AVG(b.rating), 2) AS avg_rating,
       COUNT(b.id) AS total_books
FROM authors a
JOIN book_author ba ON ba.author_id = a.id
JOIN books b ON b.id = ba.book_id
GROUP BY a.name
HAVING COUNT(b.id) >= 5
ORDER BY avg_rating ASC
LIMIT 5;
```
**Conceptos:** JOIN en cadena, GROUP BY, HAVING (filtra grupos), AVG().

---

### Consulta 3 — Categoría con mayor precio promedio
```sql
SELECT c.name AS category,
       ROUND(AVG(b.price), 2) AS avg_price,
       COUNT(b.id) AS total_books
FROM categories c
JOIN books b ON b.category_id = c.id
GROUP BY c.name
ORDER BY avg_price DESC
LIMIT 10;
```
**Conceptos:** JOIN simple, GROUP BY, AVG(), ORDER BY DESC.

---

### Consulta 4 — Top 5 autores con más libros
```sql
SELECT a.name, COUNT(b.id) AS total_books
FROM authors a
JOIN book_author ba ON ba.author_id = a.id
JOIN books b ON b.id = ba.book_id
WHERE a.name != 'Unknown'
GROUP BY a.name
ORDER BY total_books DESC
LIMIT 5;
```
**Conceptos:** JOIN en cadena N:M, COUNT(), filtrar con WHERE antes de agrupar.

---

### Consulta 5 — País con más libros rating > 3 (OBLIGATORIA)
```sql
SELECT a.country,
       COUNT(b.id) AS total_books,
       ROUND(AVG(b.rating), 2) AS avg_rating
FROM books b
JOIN book_author ba ON ba.book_id = b.id
JOIN authors a ON a.id = ba.author_id
WHERE b.rating > 3 AND a.country IS NOT NULL
GROUP BY a.country
ORDER BY total_books DESC
LIMIT 10;
```
**Conceptos:** JOIN en cadena books→book_author→authors, IS NOT NULL, GROUP BY país.
Esta consulta solo existe porque la API enriqueció los autores con datos de país.

---

## ⚡ Indexación y performance

```sql
-- Consulta lenta (Sequential Scan sin índice)
SELECT b.title, b.price, b.rating, c.name
FROM books b
JOIN categories c ON c.id = b.category_id
WHERE b.rating = 5 AND b.price < 20
ORDER BY b.price ASC;

-- Crear índice compuesto
CREATE INDEX IF NOT EXISTS idx_books_rating_price ON books(rating, price);

-- Misma consulta → ahora usa Index Scan
-- Verificar con:
EXPLAIN ANALYZE SELECT ...;
```

### ¿Por qué el índice ayuda?
Sin índice → PostgreSQL lee **todas** las filas (Seq Scan).
Con índice → va directo a las filas que cumplen la condición (Index Scan).
Es como el índice de un libro vs leer página por página.

---

## 🔢 Resultados del pipeline

| Métrica | Valor |
|---------|-------|
| Categorías scrapeadas | ~50 |
| Libros scrapeados | ~1000 |
| Autores únicos | ~952 |
| Autores encontrados en API | ~45.2% |
| Autores no encontrados (NULL) | ~54.8% |
| Tiempo estimado del pipeline | ~25 minutos |

---

## ⚠️ Decisiones de diseño importantes

1. **Un solo `commit()` al final** → más eficiente que commit por fila
2. **`ON CONFLICT DO NOTHING`** → idempotente, podés correr el script dos veces
3. **Cache en memoria** → evita llamadas HTTP duplicadas para el mismo autor
4. **`time.sleep()`** → respeta el rate limit de Open Library
5. **`RETURNING id`** → evita un SELECT extra después de cada INSERT
6. **NULLs son datos válidos** → el 54.8% sin autor es realidad de la API, no un bug
