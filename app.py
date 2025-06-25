import streamlit as st
import pandas as pd
from logic import evaluate_discrepancy

st.set_page_config(page_title="📦 Smart Cycle-Count Scanner", layout="centered")

st.title("📦 Smart Cycle-Count Scanner")
st.caption("Scan items, count inventory, flag discrepancies, and prep for syncing.")

df = pd.read_csv("data/smart_cycle_data.csv")

# Select item to simulate scan
item = st.selectbox("Select scanned item (mocked)", df["Description"])

if item:
    row = df[df["Description"] == item].iloc[0]
    st.write(f"**SKU**: {row['SKU']}  \n**Expected**: {row['expected_count']}  \n**Threshold**: {row['threshold']}")
    
    quantity = st.number_input("Enter scanned quantity", min_value=0, value=int(row["quantity"]))

    if st.button("Evaluate"):
        flagged, message = evaluate_discrepancy(quantity, row["expected_count"], str(row["threshold"]))
        st.markdown(message)

from sheets_sync import append_cycle_log

if st.button("Log to Google Sheets"):
    status = "Discrepancy" if flagged else "OK"
    append_cycle_log([
        row["SKU"],
        row["Description"],
        row["location_id"],
        quantity,
        row["expected_count"],
        quantity - row["expected_count"],
        status
    ])
    st.success("✅ Logged to Google Sheets")