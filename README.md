# 📚 Books Scraping Pipeline — Challenge 4

Pipeline de datos completo que scrapea [Books to Scrape](https://books.toscrape.com/), enriquece los autores con APIs externas y persiste todo en una base de datos relacional.

---

## ¿Qué hace?

1. **Scraping** — extrae todas las categorías y ~1000 libros del sitio
2. **Enriquecimiento** — consulta Open Library y Wikipedia para obtener datos de cada autor
3. **Persistencia** — guarda todo en SQLite con un modelo relacional N:M
4. **Análisis** — 5 consultas SQL comentadas + indexación con análisis de performance

---

## Requisitos

```bash
pip install requests beautifulsoup4 jupyter
```

SQLite viene incluido en Python. No requiere instalación adicional.

---

## Cómo ejecutar

```bash
#Instalar dependencias
pip install requests beautifulsoup4 jupyter

#Crear la base de datos
python DDL.py

# 4. Abrir el notebook
jupyter notebook pipelinev2.ipynb
```

Ejecutar las celdas en orden de arriba hacia abajo.

> ⚠️ La celda de enriquecimiento con APIs tarda ~15-20 minutos por las pausas necesarias para respetar el rate limit de Wikipedia.

---

## Estructura del proyecto

```
├── pipelinev2.ipynb      # notebook principal con todo el pipeline
├── DDL.py                # crea las 4 tablas en SQLite
├── consultas.sql         # consultas en sql apartado
├── books_pipeline.db     # base de datos generada (se crea al ejecutar)
└── README.md
```

---

## Modelo de base de datos

```
categories ──< books >──── book_author ────< authors
```

Cardinalidad:

- `categories` → `books`: uno a muchos
- `books` ↔ `authors`: muchos a muchos via `book_author`

---

## APIs utilizadas

| API          | Uso                                                    |
| ------------ | ------------------------------------------------------ |
| Open Library | Nombre del autor, año de nacimiento, cantidad de obras |
| Wikipedia    | Nacionalidad del autor                                 |
