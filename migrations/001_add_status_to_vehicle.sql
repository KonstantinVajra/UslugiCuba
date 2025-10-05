-- Миграция для добавления колонки `status` в таблицу `svc.vehicle`.
-- Эта колонка необходима для отслеживания состояния автомобиля (например, 'draft', 'published', 'archived').
-- Ошибка `UndefinedColumnError: column v.status does not exist` возникает из-за ее отсутствия.

ALTER TABLE svc.vehicle
ADD COLUMN status VARCHAR(20) NOT NULL DEFAULT 'draft';