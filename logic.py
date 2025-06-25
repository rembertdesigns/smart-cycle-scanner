def evaluate_discrepancy(quantity, expected, threshold):
    try:
        threshold_val = float(threshold.strip('%'))
        is_percent = '%' in threshold
    except:
        return False, "Invalid threshold"

    discrepancy = quantity - expected
    if is_percent:
        if expected == 0:
            return True, "Expected count is 0 — cannot evaluate % threshold"
        percent_diff = abs(discrepancy) / expected * 100
        flagged = percent_diff > threshold_val
    else:
        flagged = abs(discrepancy) > threshold_val

    return flagged, f"{'⚠️ Discrepancy' if flagged else '✅ Within Tolerance'}: Counted {quantity}, Expected {expected}, Diff {discrepancy}"