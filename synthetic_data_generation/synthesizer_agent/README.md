# Synthesizer Agent

Модуль синтеза текстов с PII-сущностями.

## Структура

- `notebooks/` - основные эксперименты с синтезатором.
- `src/metrics_eval.py` - расчет метрик по сгенерированному JSONL.
- `outputs/` - локальные результаты синтеза (`synthesized_pii.jsonl`, `final_results.json` и т.п.). Не коммитится.

## Входные данные

Синтезатор ожидает:

- корпус текстов в `synthetic_data_generation/data/`;
- пулы сущностей в `synthetic_data_generation/data/entities_pool/`;
- промпты в `synthetic_data_generation/configs/prompts.yaml`.

Ноутбуки запускаются из папки `notebooks/`.

## Метрики

Из корня репозитория:

```bash
uv run python synthetic_data_generation/synthesizer_agent/src/metrics_eval.py
```

Скрипт читает локальный файл `synthetic_data_generation/synthesizer_agent/outputs/synthesized_pii.jsonl`.
