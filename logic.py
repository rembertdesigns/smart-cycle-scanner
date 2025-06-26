import logging
import pandas as pd

# Optional: Configure basic logging to a file (can be extended later)
logging.basicConfig(
    filename='discrepancy_log.txt',
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)

# Sensitivity rules (e.g., for higher alerting on important products)
SENSITIVE_CATEGORIES = {"concentrates", "edibles", "extracts", "vape"}

def evaluate_discrepancy(quantity, expected, threshold="0.5", sku=None, category=None, name=None):
    """
    Evaluates if the counted quantity deviates beyond the threshold.
    Logs the result and recommends actions if necessary.

    Returns:
        (bool, str, str): (flagged, message, recommended_action)
    """
    try:
        threshold_val = float(threshold.strip('%'))
        is_percent = '%' in threshold
    except:
        return False, "❌ Invalid threshold format", "🚫 Check threshold config"

    discrepancy = quantity - expected
    flagged = False
    msg = ""
    action = "✅ No action needed"

    if is_percent:
        if expected == 0:
            flagged = True
            msg = "⚠️ Expected count is 0 — cannot evaluate % threshold"
            action = "🔎 Manual review required"
        else:
            percent_diff = abs(discrepancy) / expected * 100
            flagged = percent_diff > threshold_val
            msg = f"{'⚠️ Discrepancy' if flagged else '✅ OK'}: Counted {quantity}, Expected {expected}, Diff {discrepancy} ({percent_diff:.1f}%)"
    else:
        flagged = abs(discrepancy) > threshold_val
        msg = f"{'⚠️ Discrepancy' if flagged else '✅ OK'}: Counted {quantity}, Expected {expected}, Diff {discrepancy}"

    # Recommend action
    if flagged:
        if abs(discrepancy) > 5:
            action = "📹 Pull security footage & check sales logs"
        elif category and category.lower() in SENSITIVE_CATEGORIES:
            action = "🧾 Verify receipts and system logs"
        else:
            action = "🕵️ Flag for manager investigation"

    # Optional logging
    log_entry = f"[{sku or 'Unknown SKU'}] {name or 'Unnamed'} | {msg} | Action: {action}"
    logging.info(log_entry)

    return flagged, msg, action

def get_severity_score(discrepancy, expected, product_type):
    """
    Returns a numerical severity score (1–5) for triaging discrepancies.

    5 = High risk (e.g., >5 unit variance or sensitive product)
    4 = Sensitive category with any discrepancy
    3 = Medium discrepancy (>2 units)
    2 = Small discrepancy (<=2 units)
    1 = No discrepancy
    """
    if abs(discrepancy) > 5:
        return 5
    elif product_type and product_type.lower() in ["vape cartridge", "concentrate", "extract"] and abs(discrepancy) > 0:
        return 4
    elif abs(discrepancy) > 2:
        return 3
    elif abs(discrepancy) > 0:
        return 2
    return 1

def compute_severity(counted, expected):
    """
    Returns severity level based on discrepancy percentage.
    """
    if expected == 0:
        return "Critical"

    diff = abs(counted - expected)
    pct = diff / expected * 100

    if pct < 5:
        return "Trivial"
    elif pct < 10:
        return "Low"
    elif pct < 25:
        return "Medium"
    elif pct < 50:
        return "High"
    else:
        return "Critical"

def filter_by_role(df, role="admin"):
    """
    Filters discrepancies by severity based on user role.
    """
    if "severity" not in df.columns:
        return df

    role = role.lower()
    if role == "frontline":
        return df[df["severity"].isin(["High", "Critical"])]
    elif role == "manager":
        return df[df["severity"].isin(["Medium", "High", "Critical"])]
    else:
        return df  # admin sees everything
