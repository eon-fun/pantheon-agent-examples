-- Удаление всех таблиц и их зависимостей
DROP TABLE IF EXISTS user_tweet_matches CASCADE;
DROP TABLE IF EXISTS posted_tweets CASCADE;
DROP TABLE IF EXISTS tweets_history CASCADE;
DROP TABLE IF EXISTS user_tracked_accounts CASCADE;
DROP TABLE IF EXISTS tracked_accounts CASCADE;
DROP TABLE IF EXISTS users CASCADE;

-- Таблица пользователей
CREATE TABLE users (
    id BIGINT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    persona_descriptor TEXT DEFAULT NULL,
    prompt TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT now()
);

-- Таблица отслеживаемых аккаунтов
CREATE TABLE tracked_accounts (
    id SERIAL PRIMARY KEY,
    twitter_handle VARCHAR(255) UNIQUE NOT NULL,
    last_checked TIMESTAMP DEFAULT now()
);

-- Таблица отслеживаемых аккаунтов пользователями
CREATE TABLE user_tracked_accounts (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    twitter_handle VARCHAR(255) NOT NULL REFERENCES tracked_accounts(twitter_handle) ON DELETE CASCADE,
    added_at TIMESTAMP DEFAULT now(),
    UNIQUE(user_id, twitter_handle)
);

-- История твитов отслеживаемых аккаунтов
CREATE TABLE tweets_history (
    id SERIAL PRIMARY KEY,
    account_id INTEGER REFERENCES tracked_accounts(id) ON DELETE CASCADE,
    tweet_id VARCHAR(255) UNIQUE NOT NULL,
    tweet_text TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    fetched_at TIMESTAMP DEFAULT now()
);

-- История запощенных твитов ботом
CREATE TABLE posted_tweets (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    source_tweet_id VARCHAR(255) REFERENCES tweets_history(tweet_id) ON DELETE SET NULL,
    source_account_id INTEGER REFERENCES tracked_accounts(id) ON DELETE SET NULL,
    is_send BOOLEAN DEFAULT FALSE,
    posted_text TEXT NOT NULL,
    posted_at TIMESTAMP DEFAULT now()
);

-- Таблица для связи пользователей и твитов с флагом обработки
CREATE TABLE user_tweet_matches (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
    tweet_id VARCHAR(255) REFERENCES tweets_history(tweet_id) ON DELETE CASCADE,
    is_processed BOOLEAN DEFAULT FALSE,
    matched_at TIMESTAMP DEFAULT now(),
    UNIQUE(user_id, tweet_id)
);
