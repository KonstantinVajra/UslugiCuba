CREATE TABLE car_orders (
    id SERIAL PRIMARY KEY,
    car_id INTEGER REFERENCES cars(id),
    client_name TEXT NOT NULL,
    client_phone TEXT NOT NULL,
    client_comment TEXT,
    client_tg_id BIGINT,
    status TEXT DEFAULT 'new',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now()
);