-- ARIN Platform - Audit Logs Database Schema
-- Схема для хранения audit логов в TimescaleDB

CREATE TABLE IF NOT EXISTS audit_logs (
    id BIGSERIAL PRIMARY KEY,
    timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    event_type VARCHAR(50) NOT NULL,
    user_id VARCHAR(255),
    username VARCHAR(255),
    resource_type VARCHAR(100),
    resource_id VARCHAR(255),
    action TEXT,
    details JSONB,
    ip_address INET,
    user_agent TEXT,
    success BOOLEAN DEFAULT TRUE,
    error_message TEXT
);

-- Создание hypertable для TimescaleDB
SELECT create_hypertable('audit_logs', 'timestamp', if_not_exists => TRUE);

-- Индексы для быстрого поиска
CREATE INDEX IF NOT EXISTS idx_audit_logs_timestamp ON audit_logs (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_audit_logs_user_id ON audit_logs (user_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_event_type ON audit_logs (event_type);
CREATE INDEX IF NOT EXISTS idx_audit_logs_resource ON audit_logs (resource_type, resource_id);
CREATE INDEX IF NOT EXISTS idx_audit_logs_success ON audit_logs (success);

-- Retention policy (автоматическое удаление логов старше 3 лет)
SELECT add_retention_policy('audit_logs', INTERVAL '3 years', if_not_exists => TRUE);

-- Continuous aggregate для статистики (опционально)
CREATE MATERIALIZED VIEW IF NOT EXISTS audit_logs_daily
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', timestamp) AS day,
    event_type,
    COUNT(*) AS event_count,
    COUNT(*) FILTER (WHERE success = TRUE) AS success_count,
    COUNT(*) FILTER (WHERE success = FALSE) AS failed_count
FROM audit_logs
GROUP BY day, event_type;

-- Автоматическое обновление continuous aggregate
SELECT add_continuous_aggregate_policy('audit_logs_daily',
    start_offset => INTERVAL '1 month',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour',
    if_not_exists => TRUE);

