#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import re
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

from bs4 import BeautifulSoup


DEFAULT_BASE_URL = "https://2ch.su"
USER_AGENT = "kitoboy-pii-research/0.1"
POPULAR_BOARDS = ["b", "soc", "po", "wrk", "hw", "biz", "dev", "mobi", "pr", "ra", "rf", "un"]
ALL_BOARDS = [
    "a",
    "abu",
    "b",
    "bg",
    "bi",
    "biz",
    "bo",
    "c",
    "cg",
    "d",
    "de",
    "di",
    "diy",
    "em",
    "fa",
    "fag",
    "fg",
    "fl",
    "fs",
    "ftb",
    "gd",
    "hh",
    "hi",
    "hw",
    "ja",
    "me",
    "mg",
    "mlp",
    "mo",
    "mobi",
    "mov",
    "mu",
    "ne",
    "news",
    "pa",
    "p",
    "po",
    "pr",
    "psy",
    "ra",
    "re",
    "rf",
    "s",
    "sf",
    "sn",
    "soc",
    "spc",
    "sp",
    "td",
    "tr",
    "tv",
    "un",
    "vg",
    "w",
    "wh",
    "wm",
    "wp",
    "wrk",
]


def clean_comment(raw_html: str | None) -> str:
    if not raw_html:
        return ""

    normalized = raw_html.replace("<br>", "\n").replace("<br/>", "\n").replace("<br />", "\n")
    soup = BeautifulSoup(normalized, "html.parser")

    for quote in soup.select("span.quote"):
        quote.decompose()

    text = html.unescape(soup.get_text("\n"))
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text.strip()


def get_json(url: str, sleep_s: float, timeout_s: float) -> dict[str, Any]:
    time.sleep(sleep_s)
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=timeout_s) as response:
        return json.loads(response.read().decode("utf-8"))


def fetch_board_threads(
    base_url: str,
    board: str,
    threads_per_board: int,
    sleep_s: float,
    timeout_s: float,
) -> list[int]:
    payload = get_json(f"{base_url}/{board}/threads.json", sleep_s, timeout_s)
    threads = payload.get("threads", [])
    nums = []
    for item in threads:
        num = item.get("num") or item.get("thread_num")
        if num is not None:
            nums.append(int(num))
    if threads_per_board <= 0:
        return nums
    return nums[:threads_per_board]


def extract_posts(thread_payload: dict[str, Any]) -> list[dict[str, Any]]:
    if "threads" in thread_payload and thread_payload["threads"]:
        posts = thread_payload["threads"][0].get("posts", [])
    else:
        posts = thread_payload.get("posts", [])
    return posts or []


def post_record(board: str, thread_num: int, post: dict[str, Any]) -> dict[str, Any] | None:
    text = clean_comment(post.get("comment"))
    subject = clean_comment(post.get("subject"))
    if not text and not subject:
        return None

    full_text = f"{subject}\n{text}".strip() if subject else text
    stable_id = hashlib.sha256(f"2ch:{board}:{thread_num}:{post.get('num')}:{full_text}".encode("utf-8")).hexdigest()
    return {
        "id": stable_id,
        "source": "2ch.hk",
        "board": board,
        "thread_num": thread_num,
        "post_num": post.get("num"),
        "timestamp": post.get("timestamp"),
        "date": post.get("date"),
        "name": post.get("name"),
        "text": full_text,
        "text_len": len(full_text),
    }


def append_jsonl(path: Path, records: list[dict[str, Any]]) -> None:
    with path.open("a", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_seen_ids(path: Path) -> set[str]:
    seen_ids: set[str] = set()
    if not path.exists():
        return seen_ids

    with path.open("r", encoding="utf-8") as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue
            if record_id := record.get("id"):
                seen_ids.add(record_id)
    return seen_ids


def load_state(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"scraped_threads": [], "cycles_finished": 0}
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {"scraped_threads": [], "cycles_finished": 0}


def save_state(path: Path, state: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp_path = path.with_suffix(path.suffix + ".tmp")
    tmp_path.write_text(json.dumps(state, ensure_ascii=False, indent=2), encoding="utf-8")
    tmp_path.replace(path)


def choose_boards(args: argparse.Namespace) -> list[str]:
    if args.all_boards:
        return ALL_BOARDS
    if args.boards:
        return [board.strip().strip("/") for board in args.boards.split(",") if board.strip()]
    return POPULAR_BOARDS


def deadline_from_minutes(minutes: float) -> float | None:
    if minutes <= 0:
        return None
    return time.monotonic() + minutes * 60


def should_stop(total_saved: int, max_posts: int, deadline: float | None) -> bool:
    if max_posts > 0 and total_saved >= max_posts:
        return True
    return deadline is not None and time.monotonic() >= deadline


def main() -> None:
    parser = argparse.ArgumentParser(description="Скачать посты с 2ch.hk в JSONL для поиска PII-кандидатов.")
    parser.add_argument("--boards", help="Доски через запятую, например: b,soc,po. Если не указано, берутся популярные доски.")
    parser.add_argument("--all-boards", action="store_true", help="Парсить большой статический список известных досок.")
    parser.add_argument("--threads-per-board", type=int, default=0, help="0 означает все треды из threads.json.")
    parser.add_argument("--posts-per-thread", type=int, default=0, help="0 означает все посты из треда.")
    parser.add_argument("--max-posts", type=int, default=0, help="0 означает без лимита по постам.")
    parser.add_argument("--max-runtime-minutes", type=float, default=0, help="0 означает без лимита по времени.")
    parser.add_argument("--cycles", type=int, default=1, help="0 означает бесконечный цикл до лимитов/остановки.")
    parser.add_argument("--cycle-sleep", type=float, default=300.0, help="Пауза между циклами обхода досок.")
    parser.add_argument("--fresh", action="store_true", help="Перезаписать dvach_posts.jsonl перед стартом.")
    parser.add_argument("--redownload-existing-threads", action="store_true", help="Повторно скачивать треды из checkpoint/raw.")
    parser.add_argument("--state-file", type=Path, help="JSON checkpoint. По умолчанию save-dir/crawl_state.json.")
    parser.add_argument("--save-dir", type=Path, default=Path("real_pii_collection/data"))
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--sleep", type=float, default=0.35)
    parser.add_argument("--timeout", type=float, default=30.0)
    args = parser.parse_args()

    args.save_dir.mkdir(parents=True, exist_ok=True)
    raw_dir = args.save_dir / "raw_threads"
    raw_dir.mkdir(parents=True, exist_ok=True)
    output_jsonl = args.save_dir / "dvach_posts.jsonl"
    state_path = args.state_file or (args.save_dir / "crawl_state.json")
    if args.fresh:
        output_jsonl.unlink(missing_ok=True)
        state_path.unlink(missing_ok=True)

    total_saved = 0
    seen_ids = load_seen_ids(output_jsonl)
    state = load_state(state_path)
    scraped_threads = set(state.get("scraped_threads", []))
    boards = choose_boards(args)
    base_url = args.base_url.rstrip("/")
    deadline = deadline_from_minutes(args.max_runtime_minutes)
    cycle = 0

    print(f"base_url={base_url}")
    print(f"boards={','.join(boards)}")
    print(f"seen_existing={len(seen_ids)}")
    print(f"scraped_threads_checkpoint={len(scraped_threads)}")
    print(f"state={state_path}")

    while not should_stop(total_saved, args.max_posts, deadline):
        cycle += 1
        if args.cycles > 0 and cycle > args.cycles:
            break

        print(f"cycle={cycle} started")

        for board in boards:
            if should_stop(total_saved, args.max_posts, deadline):
                break

            try:
                thread_nums = fetch_board_threads(base_url, board, args.threads_per_board, args.sleep, args.timeout)
            except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                print(f"skip board {board}: {exc}")
                continue

            print(f"/{board}/ threads={len(thread_nums)}")
            for idx, thread_num in enumerate(thread_nums, start=1):
                if should_stop(total_saved, args.max_posts, deadline):
                    break

                thread_key = f"{board}:{thread_num}"
                raw_path = raw_dir / f"{board}_{thread_num}.json"
                if not args.redownload_existing_threads and (thread_key in scraped_threads or raw_path.exists()):
                    print(f"/{board}/ {idx}/{len(thread_nums)} thread={thread_num} skipped_existing")
                    continue

                url = f"{base_url}/{board}/res/{thread_num}.json"
                try:
                    payload = get_json(url, args.sleep, args.timeout)
                except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
                    print(f"skip {board}/{thread_num}: {exc}")
                    continue

                raw_path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

                records = []
                posts = extract_posts(payload)
                if args.posts_per_thread > 0:
                    posts = posts[: args.posts_per_thread]

                for post in posts:
                    record = post_record(board, thread_num, post)
                    if not record or record["id"] in seen_ids:
                        continue
                    seen_ids.add(record["id"])
                    records.append(record)
                    total_saved += 1
                    if should_stop(total_saved, args.max_posts, deadline):
                        break

                append_jsonl(output_jsonl, records)
                scraped_threads.add(thread_key)
                state.update(
                    {
                        "base_url": base_url,
                        "boards": boards,
                        "last_board": board,
                        "last_thread_num": thread_num,
                        "last_updated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "scraped_threads": sorted(scraped_threads),
                    }
                )
                save_state(state_path, state)
                print(
                    f"/{board}/ {idx}/{len(thread_nums)} thread={thread_num} "
                    f"new={len(records)} saved_this_run={total_saved} seen_total={len(seen_ids)}"
                )

        if should_stop(total_saved, args.max_posts, deadline):
            break

        if args.cycles == 0 or cycle < args.cycles:
            state["cycles_finished"] = int(state.get("cycles_finished", 0)) + 1
            save_state(state_path, state)
            print(f"cycle={cycle} finished; sleeping {args.cycle_sleep}s")
            time.sleep(args.cycle_sleep)

    print(f"saved_posts={total_saved}")
    print(f"output={output_jsonl}")


if __name__ == "__main__":
    main()
