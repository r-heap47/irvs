-- Выполняется образом postgres один раз, при первом запуске с пустым томом.
CREATE TABLE IF NOT EXISTS notes (
    id         SERIAL PRIMARY KEY,
    title      VARCHAR(200) NOT NULL,
    body       TEXT         NOT NULL DEFAULT '',
    created_at TIMESTAMPTZ  NOT NULL DEFAULT now()
);
