# 🌿 Smart Cycle Scanner

**Smart Cycle Scanner** is an AI-enhanced inventory auditing tool purpose-built for high-compliance cannabis businesses. It helps operators stay compliant with strict state-level inventory accuracy requirements (98–99%) by providing real-time cycle counts, discrepancy detection, severity scoring, and automatic reconciliation logs.

---

## 📦 Key Features

✅ **Real-Time Inventory Counting**  
Scan products and enter physical counts on the spot — results are immediately evaluated for discrepancies and logged.

⚠️ **Discrepancy Detection & Severity Scoring**  
Automatically flags mismatches between expected vs actual count with severity scores (1–5) based on risk level and product type (e.g., vape, concentrates, edibles).

🔒 **Compliance-Ready Logging**  
Every scan is synced to Google Sheets with timestamps, action recommendations, variance analysis, and role-based filtering — supporting regulatory audits and internal reviews.

📊 **Visual Dashboard for Activity Monitoring**  
Track scanned items, flagged products, and high-risk inventory from a clear activity feed with color-coded indicators.

📈 **Support for Blind Count & High-Value Alerts**  
Enable blind counting to prevent bias, or receive extra alerts for high-value product categories with known shrinkage risk.

---

## 🛠️ Tech Stack

- **Streamlit** – rapid app framework for data-driven dashboards  
- **Pandas** – data manipulation and analysis  
- **Google Sheets API** – real-time cloud syncing  
- **Python (3.12)** – backend logic and data validation  

---

## 📁 Project Structure

```plaintext
├── app.py                  # Main Streamlit UI
├── logic.py                # Discrepancy logic & severity engine
├── sheets_sync.py          # Google Sheets integration
├── smart_cycle_data.csv    # Sample inventory data
├── service_account.json    # Google Sheets credentials (generated at runtime)
├── discrepancy_log.txt     # Optional log file
└── README.md
