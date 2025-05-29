def format_combined(preds: list[str]):
    if all(x == "" for x in preds):
        return "NOT_FOUND"
    preds = [x for x in preds if x != ""]
    return ";".join(preds)
