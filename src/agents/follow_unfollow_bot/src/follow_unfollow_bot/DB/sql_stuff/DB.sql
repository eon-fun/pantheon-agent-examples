-- Удаление всех таблиц и их зависимостей
DROP TABLE IF EXISTS tracked_accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Таблица пользователей
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    followers_today INT,
    created_at TIMESTAMP DEFAULT now()
);

-- Таблица на кого подписался пользователь
CREATE TABLE tracked_accounts (
    id BIGINT PRIMARY KEY,
    user_id BIGINT REFERENCES users(id),
    created_at TIMESTAMP DEFAULT now()
);
