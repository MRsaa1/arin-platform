# ARIN Platform - ML Models

## Обзор

Система управления ML моделями с поддержкой:
- Автоматического переобучения
- Мониторинга дрифта моделей
- Оценки и сравнения моделей
- Обучения агентов на исторических данных

## Компоненты

### Model Evaluator

Система оценки моделей:

```python
from backend.ai_engine.ml_models import ModelEvaluator

evaluator = ModelEvaluator()

# Оценка классификационной модели
metrics = evaluator.evaluate_classification(
    y_true=y_test,
    y_pred=y_pred,
    y_proba=y_proba,
    model_name="credit_risk_model"
)

# Обнаружение дрифта
drift = evaluator.detect_model_drift(
    current_metrics=current_metrics,
    baseline_metrics=baseline_metrics
)
```

### Model Trainer

Система обучения и переобучения моделей:

```python
from backend.ai_engine.ml_models import ModelTrainer

trainer = ModelTrainer()

# Обучение модели
result = await trainer.train_credit_risk_model(
    training_data=df,
    test_size=0.2
)

# Автоматическое переобучение
result = await trainer.auto_retrain_if_needed(
    model_name="credit_risk_model",
    new_data=new_df
)
```

### Agent Trainer

Система обучения агентов:

```python
from backend.ai_engine.agent_learning import AgentTrainer

agent_trainer = AgentTrainer()

# Обучение на исторических данных
result = await agent_trainer.train_agent_on_history(
    agent_id="credit_risk_agent",
    historical_data=historical_tasks
)

# Continuous learning
result = await agent_trainer.continuous_learning_update(
    agent_id="credit_risk_agent",
    new_experience=new_task_result
)
```

## Улучшения моделей

### Credit Risk Model

Улучшенные параметры XGBoost:
- `n_estimators=200` (было 100)
- `max_depth=6` (было 5)
- `learning_rate=0.05` (было 0.1)
- Добавлены `subsample`, `colsample_bytree`, `min_child_weight`, `gamma`
- Early stopping для предотвращения переобучения

## API Endpoints

- `POST /api/v1/ml/train` - Обучение модели
- `POST /api/v1/ml/evaluate` - Оценка модели
- `GET /api/v1/ml/training-history` - История обучения
- `POST /api/v1/ml/agents/{agent_id}/train` - Обучение агента
- `GET /api/v1/ml/agents/{agent_id}/performance` - Метрики агента
- `POST /api/v1/ml/agents/{agent_id}/learn` - Continuous learning

## Автоматическое переобучение

Запуск скрипта автоматического переобучения:

```bash
python backend/scripts/auto_retrain_models.py
```

В production это должно запускаться по расписанию (cron, scheduler).

## Мониторинг

Система автоматически:
- Отслеживает производительность моделей
- Обнаруживает дрифт моделей
- Рекомендует переобучение при необходимости
- Ведет историю обучения и оценок

