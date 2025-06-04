def format_combined(preds: list[str]):
    """
    Formats a list of predictions into a single string.

    Args:
        preds (list[str]): List of string predictions

    Returns:
        str: Formatted string of predictions joined by semicolons.
             Returns "NOT_FOUND" if all predictions are empty strings.
    """
    if all(x == "" for x in preds):
        return "NOT_FOUND"
    preds = [x for x in preds if x != ""]
    return ";".join(preds)
