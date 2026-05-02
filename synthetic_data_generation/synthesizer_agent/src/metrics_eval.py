import json
import re
from collections import Counter
from pathlib import Path
from statistics import StatisticsError, mode

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


TAG_RE = re.compile(r"<([A-Z0-9_]+)>.*?</\1>", flags=re.DOTALL)
WS_RE = re.compile(r"\s+")


def _tagged_values(text, key):
    pattern = re.compile(rf"<{re.escape(key)}>(.*?)</{re.escape(key)}>", flags=re.DOTALL)
    return pattern.findall(text)


def compute_tag_correctness(results):
    total_texts = len(results)
    total_entities = 0
    correct_entities = 0
    strict_correct_texts = 0
    exact_mismatches = []

    for text_idx, item in enumerate(results):
        text = item["text"]
        used_entities = item["used_entities"]
        text_ok = True

        for ent_idx, ent in enumerate(used_entities):
            total_entities += 1
            key = ent["key"]
            value = ent["value"]
            expected = f"<{key}>{value}</{key}>"
            if expected in text:
                correct_entities += 1
            else:
                text_ok = False
                exact_mismatches.append(
                    {
                        "text_index": text_idx,
                        "jsonl_line": text_idx + 1,
                        "entity_index": ent_idx,
                        "key": key,
                        "value": value,
                        "expected": expected,
                        "actual_tagged_values": _tagged_values(text, key),
                        "text": text,
                        "used_entities": used_entities,
                    }
                )

        if text_ok:
            strict_correct_texts += 1

    return {
        "entity_level_score": correct_entities / total_entities if total_entities else 1.0,
        "strict_text_score": strict_correct_texts / total_texts if total_texts else 1.0,
        "total_entities": total_entities,
        "correct_entities": correct_entities,
        "total_texts": total_texts,
        "strict_correct_texts": strict_correct_texts,
        "exact_mismatches": exact_mismatches,
    }


def _normalize_for_similarity(text):
    text = TAG_RE.sub(" [PII] ", text)
    text = WS_RE.sub(" ", text.lower()).strip()
    return text


def compute_semantic_repetition(results):
    texts = [_normalize_for_similarity(x["text"]) for x in results]
    n = len(texts)

    if n <= 1:
        return {
            "num_texts": n,
            "mean_nearest_similarity": 0.0,
            "p90_nearest_similarity": 0.0,
            "p95_nearest_similarity": 0.0,
            "share_nearest_ge_0_90": 0.0,
            "share_nearest_ge_0_95": 0.0,
            "nearest_similarity_values": [],
            "method": "tfidf_char_ngrams_cosine",
        }

    vectorizer = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5))
    matrix = vectorizer.fit_transform(texts)
    sim = cosine_similarity(matrix)
    np.fill_diagonal(sim, -1.0)
    nearest = sim.max(axis=1)

    return {
        "num_texts": n,
        "mean_nearest_similarity": float(np.mean(nearest)),
        "p90_nearest_similarity": float(np.quantile(nearest, 0.9)),
        "p95_nearest_similarity": float(np.quantile(nearest, 0.95)),
        "share_nearest_ge_0_90": float(np.mean(nearest >= 0.90)),
        "share_nearest_ge_0_95": float(np.mean(nearest >= 0.95)),
        "nearest_similarity_values": [float(x) for x in nearest.tolist()],
        "method": "tfidf_char_ngrams_cosine",
    }





def compute_dataset_stats(results):
    entity_counts = [len(item.get("used_entities", [])) for item in results]
    entity_type_counts = Counter(
        ent.get("key")
        for item in results
        for ent in item.get("used_entities", [])
        if ent.get("key")
    )
    count_distribution = Counter(entity_counts)

    if entity_counts:
        try:
            entities_per_text_mode = mode(entity_counts)
        except StatisticsError: # ручной подсчет моды:
            # сначала по частоте по убыванию: -x[1]
            # при равной частоте по числу сущностей по возрастанию: x[0]
            entities_per_text_mode = sorted(count_distribution.items(), key=lambda x: (-x[1], x[0]))[0][0]

        entities_per_text = {
            "min": int(min(entity_counts)),
            "max": int(max(entity_counts)),
            "mean": float(np.mean(entity_counts)),
            "median": float(np.median(entity_counts)),
            "mode": int(entities_per_text_mode),
            "distribution": {int(k): int(v) for k, v in sorted(count_distribution.items())},
        }
    else:
        entities_per_text = {
            "min": 0,
            "max": 0,
            "mean": 0.0,
            "median": 0.0,
            "mode": 0,
            "distribution": {},
        }

    total_texts = len(results)
    total_entities = sum(entity_counts)
    texts_with_entities = sum(1 for count in entity_counts if count > 0)

    return {
        "total_texts": total_texts,
        "total_entities": total_entities,
        "texts_with_entities": texts_with_entities,
        "texts_without_entities": total_texts - texts_with_entities,
        "entities_per_text": entities_per_text,
        "entity_type_counts": dict(sorted(entity_type_counts.items())),
    }

def compute_all_metrics(results):
    return {
        "dataset_stats": compute_dataset_stats(results),
        "tag_correctness": compute_tag_correctness(results),
        "semantic_repetition": compute_semantic_repetition(results),
    }


def load_jsonl(path):
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def main():
    base_dir = Path(__file__).resolve().parents[1]
    results = load_jsonl(base_dir / "outputs" / "synthesized_pii.jsonl")
    report = compute_all_metrics(results)
    print(report['dataset_stats'])


if __name__ == "__main__":
    main()
