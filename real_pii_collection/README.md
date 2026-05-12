# real_pii_collection

Мини-пайплайн для сбора публичных сообщений с 2ch.hk и первичного поиска кандидатов на реальные PII через Mistral.

Идея вдохновлена `mr8bit/dvach_parse`: сначала скачиваем треды с выбранных досок, затем нормализуем посты в JSONL. В отличие от оригинального скрипта, здесь есть лимиты на число тредов/постов и отдельный выходной файл для LLM-фильтрации.

## Сбор сообщений

Запуск из корня репозитория через проектное окружение:

```bash
uv run python real_pii_collection/scripts/scrape_dvach.py \
  --boards b,soc,po \
  --threads-per-board 20 \
  --posts-per-thread 150 \
  --max-posts 3000 \
  --save-dir real_pii_collection/data
```

По умолчанию используется `https://2ch.su`, потому что `2ch.hk` сейчас может редиректить на HTML-страницу вместо JSON API. Если нужно, домен можно поменять:

```bash
uv run python real_pii_collection/scripts/scrape_dvach.py --base-url https://2ch.hk --boards b
```

Результаты:

- `real_pii_collection/data/raw_threads/` - исходные JSON тредов.
- `real_pii_collection/data/dvach_posts.jsonl` - очищенные посты для дальнейшей фильтрации.
- `real_pii_collection/data/crawl_state.json` - checkpoint для продолжения без повторного скачивания уже обработанных тредов.

Файлы `*.json`, `*.jsonl`, `*.csv` уже игнорируются в корневом `.gitignore`, так что raw-корпус не должен случайно попасть в git.

## Долгий сбор

Запустить на час по большому списку досок:

```bash
uv run python real_pii_collection/scripts/scrape_dvach.py \
  --all-boards \
  --threads-per-board 0 \
  --posts-per-thread 0 \
  --max-runtime-minutes 60 \
  --cycles 0 \
  --cycle-sleep 300 \
  --save-dir real_pii_collection/data
```

На следующий день можно запустить ту же команду: скрипт загрузит `crawl_state.json`, прочитает уже существующий `dvach_posts.jsonl` и пропустит треды, которые уже были скачаны.

Если нужно начать с нуля:

```bash
uv run python real_pii_collection/scripts/scrape_dvach.py --all-boards --fresh
```

Если нужно принудительно перекачать уже обработанные треды:

```bash
uv run python real_pii_collection/scripts/scrape_dvach.py --all-boards --redownload-existing-threads
```

## LLM-фильтр

Открой `real_pii_collection/notebooks/pii_candidate_filter_mistral.ipynb`, задай `INPUT_JSONL`, `MAX_ROWS` и запусти ячейки.

По умолчанию ноутбук читает:

```text
real_pii_collection/data/dvach_posts.jsonl
```

И сохраняет:

```text
real_pii_collection/data/outputs/pii_candidates_llm.jsonl
real_pii_collection/data/outputs/pii_candidates_llm.csv
```

Используется ключ `MISTRAL_API_KEY` из корневого `.env`.
