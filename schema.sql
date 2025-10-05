-- Создаем схему, если она не существует
CREATE SCHEMA IF NOT EXISTS svc;

-- Таблица пользователей. Нужна для связи с провайдерами.
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
    name TEXT, -- Имя провайдера, будет задаваться админом
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица услуг.
CREATE TABLE IF NOT EXISTS svc.service (
    id SERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    category TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Обновленная таблица транспортных средств.
CREATE TABLE IF NOT EXISTS svc.vehicle (
    id SERIAL PRIMARY KEY,
    provider_id INTEGER NOT NULL REFERENCES svc.provider(id) ON DELETE CASCADE,
    title TEXT, -- Название карточки, например "Chevrolet Bel Air, 1957, белый"
    description TEXT, -- Краткое описание
    photo_file_ids TEXT[] NOT NULL, -- Массив file_id для фотографий
    seats INTEGER, -- Количество мест
    price_per_hour NUMERIC,
    price_details TEXT, -- Например, "По запросу"
    status TEXT NOT NULL DEFAULT 'draft', -- 'draft', 'pending_moderation', 'published', 'archived'
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

-- Таблица заказов (оставим для будущего расширения, но в текущем флоу не используется).
CREATE TABLE IF NOT EXISTS svc.order (
    id SERIAL PRIMARY KEY,
    client_user_id INTEGER NOT NULL REFERENCES svc.user(id),
    vehicle_id INTEGER REFERENCES svc.vehicle(id),
    price NUMERIC,
    status TEXT NOT NULL DEFAULT 'new', -- 'new', 'confirmed', 'rejected', 'completed'
    client_comment TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

-- Добавим одну услугу для аренды авто, чтобы система могла с ней работать.
INSERT INTO svc.service (id, title, category) VALUES (1, 'Аренда ретро-авто с водителем', 'transport') ON CONFLICT (id) DO NOTHING;