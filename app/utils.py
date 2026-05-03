def merge_entities(entity_groups: list[list[dict]]) -> list[dict]:
    """
    Merge entity spans returned by several extractors for the same text.

    Exact duplicates are removed, then entities are sorted by span position.
    """
    merged = []
    seen = set()

    for entities in entity_groups:
        for entity in entities:
            key = (
                entity["start"],
                entity["end"],
                entity["label"],
                entity["text"],
            )
            if key in seen:
                continue
            seen.add(key)
            merged.append(entity)

    return sorted(merged, key=lambda x: (x["start"], x["end"], x["label"], x["text"]))
