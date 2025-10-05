CREATE TABLE cars (
    id SERIAL PRIMARY KEY,
    name TEXT,
    brand TEXT,
    model TEXT,
    year INTEGER,
    color TEXT,
    engine TEXT,
    transmission TEXT,
    fuel TEXT,
    price NUMERIC,
    image_url TEXT,
    description TEXT,
    status TEXT DEFAULT 'draft',
    created_at TIMESTAMP DEFAULT now(),
    updated_at TIMESTAMP DEFAULT now()
);