-- Создаем схему, если она не существует, чтобы избежать конфликтов.
CREATE SCHEMA IF NOT EXISTS svc;

-- Таблица пользователей. Хранит основную информацию и роли.
CREATE TABLE IF NOT EXISTS svc.user (
    id SERIAL PRIMARY KEY,
    tg_id BIGINT UNIQUE NOT NULL,
    role TEXT NOT NULL DEFAULT 'client', -- 'client', 'provider', 'admin'
    is_banned BOOLEAN DEFAULT FALSE,
    joined_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица поставщиков услуг. Связана с пользователями.
CREATE TABLE IF NOT EXISTS svc.provider (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES svc.user(id) ON DELETE CASCADE,
    name TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица услуг. Определяет, какие услуги предоставляет сервис.
CREATE TABLE IF NOT EXISTS svc.service (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица транспортных средств. Принадлежит конкретному поставщику.
CREATE TABLE IF NOT EXISTS svc.vehicle (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES svc.provider(id) ON DELETE CASCADE,
    make TEXT, -- Марка
    model TEXT, -- Модель
    year INTEGER,
    color TEXT,
    engine TEXT,
    transmission TEXT,
    fuel TEXT,
    price NUMERIC,
    photo_url TEXT,
    description TEXT,
    is_approved BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица заказов. Связывает клиента, услугу, транспорт и поставщика.
CREATE TABLE IF NOT EXISTS svc.order (
    id SERIAL PRIMARY KEY,
    client_user_id INTEGER NOT NULL REFERENCES svc.user(id),
    provider_id INTEGER NOT NULL REFERENCES svc.provider(id),
    service_id INTEGER NOT NULL REFERENCES svc.service(id),
    vehicle_id INTEGER REFERENCES svc.vehicle(id), -- Может быть NULL, если услуга не требует авто
    pickup_location TEXT,
    dropoff_location TEXT,
    scheduled_at TIMESTAMPTZ,
    price NUMERIC,
    status TEXT NOT NULL DEFAULT 'new', -- 'new', 'approved', 'rejected', 'in_progress', 'completed'
    client_comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Добавим одну услугу для аренды авто, чтобы система могла с ней работать.
INSERT INTO svc.service (id, title, category) VALUES (1, 'Аренда кабриолета с водителем', 'transport') ON CONFLICT (id) DO NOTHING;