# ARIN Platform - Security Implementation

## 🔒 Реализованные компоненты безопасности

### 1. Аутентификация и авторизация

#### JWT Authentication
- **Файл**: `backend/auth/jwt_handler.py`
- JWT токены с настраиваемым временем жизни
- Поддержка OAuth2 password flow
- Верификация токенов

**Использование**:
```python
from backend.auth.jwt_handler import get_current_user, TokenData

@router.get("/protected")
async def protected_route(current_user: TokenData = Depends(get_current_user)):
    return {"user": current_user.username}
```

#### OAuth 2.0
- **Файл**: `backend/auth/oauth.py`
- Поддержка GitHub и Google OAuth
- Верификация токенов через провайдеров

#### Password Handling
- **Файл**: `backend/auth/password_handler.py`
- Bcrypt хеширование паролей
- Безопасная проверка паролей

### 2. Role-Based Access Control (RBAC)

- **Файл**: `backend/auth/rbac.py`
- 4 роли: Admin, Analyst, Viewer, API User
- 15+ разрешений
- Dependency injection для проверки прав

**Роли и разрешения**:
- **Admin**: Все разрешения
- **Analyst**: Просмотр и анализ
- **Viewer**: Только просмотр
- **API User**: API доступ

**Использование**:
```python
from backend.auth.rbac import require_permission, Permission

@router.post("/risks/analyze")
async def analyze_risk(
    current_user: TokenData = Depends(require_permission(Permission.ANALYZE_RISKS))
):
    # Только пользователи с разрешением ANALYZE_RISKS могут выполнить
    pass
```

### 3. API Keys Management

- **Файл**: `backend/auth/api_keys.py`
- Генерация безопасных API ключей
- Хеширование ключей (bcrypt)
- Управление жизненным циклом (создание, отзыв)
- Ограничение по времени (expiration)

**API Endpoints**:
- `POST /api/v1/auth/api-keys` - Создание ключа
- `GET /api/v1/auth/api-keys` - Список ключей
- `DELETE /api/v1/auth/api-keys/{key_id}` - Отзыв ключа

### 4. Data Encryption

- **Файл**: `backend/security/encryption.py`
- Шифрование данных at rest
- Использование Fernet (symmetric encryption)
- PBKDF2 для генерации ключей

**Использование**:
```python
from backend.security.encryption import data_encryption

# Шифрование
encrypted = data_encryption.encrypt("sensitive data")

# Расшифровка
decrypted = data_encryption.decrypt(encrypted)
```

### 5. Secrets Management

- **Файл**: `backend/security/secrets_manager.py`
- Поддержка нескольких backends:
  - Local (development)
  - HashiCorp Vault (production)
  - AWS Secrets Manager (альтернатива)
- Ротация секретов

**Использование**:
```python
from backend.security.secrets_manager import secrets_manager

api_key = secrets_manager.get_secret("OPENAI_API_KEY")
```

### 6. TLS/SSL Configuration

- **Файл**: `infrastructure/nginx/nginx-ssl.conf`
- TLS 1.2 и 1.3
- Security headers (HSTS, X-Frame-Options, etc.)
- HTTP to HTTPS redirect

## 🔐 API Endpoints для аутентификации

### Регистрация
```bash
POST /api/v1/auth/register
{
  "username": "user",
  "email": "user@example.com",
  "password": "secure_password"
}
```

### Вход
```bash
POST /api/v1/auth/login
# OAuth2 password flow
username=user&password=secure_password
```

### OAuth вход
```bash
POST /api/v1/auth/oauth
{
  "provider": "github",
  "token": "oauth_token"
}
```

### Получение информации о пользователе
```bash
GET /api/v1/auth/me
Authorization: Bearer <token>
```

## 🛡️ Best Practices

1. **Всегда используйте HTTPS** в production
2. **Храните секреты в переменных окружения** или secrets manager
3. **Используйте RBAC** для контроля доступа
4. **Ротируйте API ключи** регулярно
5. **Логируйте все действия** (audit logs)
6. **Используйте сильные пароли** (минимум 12 символов)
7. **Ограничивайте rate limiting** для API endpoints

## 📋 Checklist для production

- [ ] Настроить TLS/SSL сертификаты
- [ ] Настроить HashiCorp Vault или AWS Secrets Manager
- [ ] Включить HTTPS redirect
- [ ] Настроить security headers
- [ ] Реализовать audit logging
- [ ] Настроить ротацию ключей
- [ ] Провести security audit
- [ ] Настроить monitoring для подозрительной активности

## 🔄 Следующие шаги

- Audit logs (Неделя 31-32)
- Compliance (GDPR, SOC 2)
- Data retention policies

