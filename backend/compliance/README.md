# ARIN Platform - Compliance Module

## Обзор

Модуль compliance обеспечивает:
- Audit logging всех действий
- GDPR compliance
- Data retention policies
- Backup и recovery

## Компоненты

### 1. Audit Logger

Автоматическое логирование всех действий в системе.

**Использование**:
```python
from backend.compliance.audit_logger import audit_logger, AuditEventType

audit_logger.log_event(
    event_type=AuditEventType.RISK_ANALYZED,
    user_id="user123",
    username="analyst",
    resource_type="risk_analysis",
    resource_id="analysis_456",
    action="analyze",
    ip_address="192.168.1.1",
    success=True
)
```

### 2. GDPR Compliance

Реализация требований GDPR:
- Right of access (Article 15)
- Right to be forgotten (Article 17)
- Data portability (Article 20)
- Right to rectification (Article 16)

### 3. Data Retention

Автоматическое управление жизненным циклом данных:
- Настраиваемые политики хранения
- Автоматическая очистка старых данных
- Поддержка различных типов данных

### 4. Backup and Recovery

Система резервного копирования:
- Full, incremental, differential backups
- Автоматическое восстановление
- Управление жизненным циклом бэкапов

## Database Schema

Схема для audit logs находится в `audit_schema.sql`.

Для применения:
```sql
\i backend/compliance/audit_schema.sql
```

## Периодические задачи

Настроены Celery задачи:
- Очистка старых данных: ежедневно в 3:00
- Создание бэкапа: ежедневно в 2:00
- Очистка старых бэкапов: еженедельно в воскресенье в 4:00

## API Endpoints

Все endpoints требуют аутентификации и соответствующих разрешений.

См. `backend/api/routes/compliance.py` для полного списка endpoints.

