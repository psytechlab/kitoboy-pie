# Synthesizer Agent

Модуль синтеза текстов с PII-сущностями.

## Структура

- `notebooks/synthesizer_agent.ipynb` - основной ноутбук синтезатора.
- `notebooks/dataset_analysis.ipynb` - анализ накопленного JSONL: метрики, exact mismatches, похожие пары и ручной просмотр примеров.
- `src/metrics_eval.py` - расчет метрик по сгенерированному JSONL.
- `outputs/synthesized_pii.jsonl` - общий накопительный датасет. Не коммитится.
- `outputs/history/` - JSONL-файлы отдельных запусков синтезатора. Не коммитится.

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
