-- Libros con más de 3 estrellas por menos de £10
SELECT
    title,
    price,
    rating
FROM
    books
WHERE
    rating > 3
    AND price < 10
ORDER BY
    rating DESC,
    price ASC;

-- Autor con peor promedio de rating
SELECT
    a.name,
    ROUND(AVG(b.rating), 2) AS avg_rating,
    COUNT(b.id) AS total_books
FROM
    authors a
    JOIN book_author ba ON ba.author_id = a.id
    JOIN books b ON b.id = ba.book_id
GROUP BY
    a.name
HAVING
    COUNT(b.id) >= 5
ORDER BY
    avg_rating ASC
LIMIT
    5;

-- Categoría con mayor precio promedio
SELECT
    c.name AS category,
    ROUND(AVG(b.price), 2) AS avg_price,
    COUNT(b.id) AS total_books
FROM
    categories c
    JOIN books b ON b.category_id = c.id
GROUP BY
    c.name
ORDER BY
    avg_price DESC
LIMIT
    10;

-- Top 5 autores con más libros
SELECT
    a.name,
    COUNT(b.id) AS total_books
FROM
    authors a
    JOIN book_author ba ON ba.author_id = a.id
    JOIN books b ON b.id = ba.book_id
WHERE
    a.name != 'Unknown'
GROUP BY
    a.name
ORDER BY
    total_books DESC
LIMIT
    5;

-- País con más libros rating > 3
SELECT
    a.country,
    COUNT(b.id) AS total_books,
    ROUND(AVG(b.rating), 2) AS avg_rating
FROM
    books b
    JOIN book_author ba ON ba.book_id = b.id
    JOIN authors a ON a.id = ba.author_id
WHERE
    b.rating > 3
    AND a.country IS NOT NULL
GROUP BY
    a.country
ORDER BY
    total_books DESC
LIMIT
    10;
