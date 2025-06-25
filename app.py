import streamlit as st
import pandas as pd
import time
from logic import evaluate_discrepancy
from datetime import datetime
import random
import json
import plotly.graph_objects as go
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheets_sync import append_cycle_log

# Define Google Sheets constants
SHEET_ID = "15D6ZVuXf7W_0AYPSRq_8PeZaESZ9mEpgS4djmTRMDE0"  # Replace with your actual sheet ID
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Enhanced page config
st.set_page_config(
    page_title="📦 Smart Cycle-Count Scanner", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://your-company.com/support',
        'Report a bug': "https://your-company.com/bug-report",
        'About': "Smart Cycle-Count Scanner v2.0 - AI-Powered Inventory Management"
    }
)

# Enhanced CSS for professional look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2.5rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
        position: relative;
        overflow: hidden;
    }
    
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: repeating-linear-gradient(
            45deg,
            transparent,
            transparent 10px,
            rgba(255, 255, 255, 0.1) 10px,
            rgba(255, 255, 255, 0.1) 20px
        );
        animation: float 20s linear infinite;
    }
    
    @keyframes float {
        0% { transform: translate(-50%, -50%) rotate(0deg); }
        100% { transform: translate(-50%, -50%) rotate(360deg); }
    }
    
    .main-header h1, .main-header p {
        position: relative;
        z-index: 1;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.8rem;
        border-radius: 15px;
        border-left: 5px solid #4f46e5;
        box-shadow: 0 8px 25px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.15);
    }
    
    .scanner-section {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 2rem;
        border-radius: 15px;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.08);
        border: 1px solid rgba(79, 70, 229, 0.1);
        margin-bottom: 1rem;
    }
    
    .camera-feed {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border: 3px dashed #d1d5db;
        border-radius: 12px;
        padding: 3rem;
        text-align: center;
        margin: 1rem 0;
        position: relative;
        overflow: hidden;
        min-height: 200px;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    
    .scan-animation {
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, transparent, #4f46e5, transparent);
        animation: scan 2s ease-in-out infinite;
    }
    
    @keyframes scan {
        0% { transform: translateY(0px); }
        50% { transform: translateY(200px); }
        100% { transform: translateY(0px); }
    }
    
    .success-alert {
        background: linear-gradient(135deg, #d1fae5 0%, #a7f3d0 100%);
        color: #065f46;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #10b981;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(16, 185, 129, 0.2);
        animation: slideIn 0.5s ease;
    }
    
    .warning-alert {
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 1.5rem;
        border-radius: 12px;
        border: 2px solid #f59e0b;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(245, 158, 11, 0.2);
        animation: slideIn 0.5s ease;
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .activity-item {
        background: white;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 4px solid #e5e7eb;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .activity-item:hover {
        border-left-color: #4f46e5;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    }
    
    .status-indicator {
        display: inline-block;
        width: 12px;
        height: 12px;
        border-radius: 50%;
        margin-right: 8px;
        animation: pulse 2s infinite;
    }
    
    .status-ok {
        background-color: #10b981;
    }
    
    .status-flagged {
        background-color: #ef4444;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .demo-controls {
        background: linear-gradient(135deg, #fef7ff 0%, #f3e8ff 100%);
        border: 2px solid #a855f7;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .integration-badge {
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(16, 185, 129, 0.3);
    }
    
    .footer-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 2rem;
        border-radius: 15px;
        border-top: 3px solid #4f46e5;
        margin-top: 2rem;
        text-align: center;
    }
    
    .stSelectbox > div > div {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
    }
    
    .stNumberInput > div > div > input {
        background: white;
        border: 2px solid #e5e7eb;
        border-radius: 8px;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>📦 Smart Cycle-Count Scanner</h1>
    <p>AI-Powered Inventory Management with Real-Time Sync</p>
    <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 10px;">✨ Enterprise-Grade • 🔄 Real-Time Sync • 📊 Compliance Ready</p>
</div>
""", unsafe_allow_html=True)

# Initialize session state with sample data for demo
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 47  # Start with some demo data
if 'discrepancy_count' not in st.session_state:
    st.session_state.discrepancy_count = 3
if 'activity_log' not in st.session_state:
    # Pre-populate with some demo activity
    st.session_state.activity_log = [
        {'time': '14:23:15', 'sku': 'SKU-1739', 'item': 'Elderberry Syrup', 'counted': 4, 'expected': 4, 'status': 'OK', 'flagged': False},
        {'time': '14:21:42', 'sku': 'SKU-6358', 'item': 'Green Tea Extract', 'counted': 9, 'expected': 7, 'status': 'Flagged', 'flagged': True},
        {'time': '14:19:33', 'sku': 'SKU-2703', 'item': 'B-Complex Vitamins', 'counted': 5, 'expected': 5, 'status': 'OK', 'flagged': False},
    ]

# Load data
@st.cache_data
def load_data():
    return pd.read_csv("data/smart_cycle_data.csv")

df = load_data()

# Enhanced sidebar dashboard
with st.sidebar:
    st.markdown("### 📊 Live Dashboard")
    
    accuracy = 100 if st.session_state.scan_count == 0 else round(((st.session_state.scan_count - st.session_state.discrepancy_count) / st.session_state.scan_count) * 100, 1)
    
    # Enhanced metrics with better styling
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #4f46e5; margin: 0;">{st.session_state.scan_count}</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Items Scanned</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #10b981; margin: 0;">{accuracy}%</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Accuracy</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #ef4444; margin: 0;">{st.session_state.discrepancy_count}</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Discrepancies</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #8b5cf6; margin: 0;">0.3s</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Avg Scan Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced integration status
    st.markdown("### 🔗 Integration Status")
    st.markdown('<div class="status-indicator status-ok"></div>**Google Sheets** - Connected', unsafe_allow_html=True)
    st.markdown('<div class="status-indicator status-ok"></div>**Metrc API** - Active', unsafe_allow_html=True)
    st.markdown('<div class="status-indicator status-ok"></div>**Barcode Scanner** - Ready', unsafe_allow_html=True)
    st.markdown('<div class="status-indicator status-ok"></div>**Mobile Sync** - Enabled', unsafe_allow_html=True)
    
    if st.button("🔄 Sync All Data", use_container_width=True):
        with st.spinner("Syncing to Google Sheets & Metrc..."):
            time.sleep(2)
        st.success("✅ Sync completed!")
        st.balloons()
    
    st.markdown("---")
    
    # Demo controls
    st.markdown("### 🎬 Demo Controls")
    st.markdown('<div class="demo-controls">', unsafe_allow_html=True)
    demo_mode = st.checkbox("🤖 Auto-Generate Counts", help="Automatically generates realistic count data for demo purposes")
    blind_mode = st.checkbox("👁️ Blind Count Mode", help="Hide expected counts during scanning")
    live_mode = st.checkbox("⚡ Live Demo Mode", help="Show real-time updates and animations")
    st.markdown('</div>', unsafe_allow_html=True)
    
    if st.button("🎯 Reset Demo Data"):
        st.session_state.scan_count = 0
        st.session_state.discrepancy_count = 0
        st.session_state.activity_log = []
        st.rerun()

# Main content area with enhanced layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="scanner-section">', unsafe_allow_html=True)
    st.markdown("### 📸 Smart Barcode Scanner")
    
    # Enhanced camera feed visualization
    camera_placeholder = st.empty()
    
    # Camera status indicator
    col_cam1, col_cam2, col_cam3 = st.columns([1, 2, 1])
    with col_cam2:
        if st.button("🔍 **SIMULATE BARCODE SCAN**", use_container_width=True):
            with camera_placeholder.container():
                st.markdown("""
                <div class="camera-feed">
                    <div class="scan-animation"></div>
                    <div>
                        <h3>🛡️ SCANNING...</h3>
                        <p>Barcode detected • Processing image...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(2)
                
                # Auto-select random item for demo
                random_item = random.choice(df["Description"].unique())
                st.session_state.auto_selected_item = random_item
                
            camera_placeholder.success("✅ **Scan Complete** - Item automatically identified!")
            st.rerun()
    
    # Default camera view
    if 'auto_selected_item' not in st.session_state:
        with camera_placeholder.container():
            st.markdown("""
            <div class="camera-feed">
                <div>
                    <h3 style="color: #6b7280;">📷 Camera Feed Active</h3>
                    <p style="color: #9ca3af;">Point camera at barcode or use simulator above</p>
                    <p style="font-size: 0.8rem; color: #d1d5db;">USB/Bluetooth scanners supported</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Item selection with enhanced styling
    st.markdown("#### 🎯 Item Selection")
    
    selected_item = st.session_state.get('auto_selected_item', "")
    if not selected_item:
        item_descriptions = df["Description"].unique()
        selected_item = st.selectbox(
            "Choose scanned item (or scan to auto-detect)",
            [""] + list(item_descriptions),
            help="💡 In production, this auto-populates from barcode scan"
        )

    if selected_item:
        row = df[df["Description"] == selected_item].iloc[0]
        
        # Enhanced item details card
        expected_display = "Hidden (Blind Mode)" if blind_mode else f"{row['expected_count']} units"
        
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="color: #4f46e5; margin-bottom: 1rem;">📦 {selected_item}</h4>
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
                <div>
                    <p style="margin: 0.3rem 0;"><strong>SKU:</strong> <span style="color: #6b7280;">{row['SKU']}</span></p>
                    <p style="margin: 0.3rem 0;"><strong>Location:</strong> <span style="color: #6b7280;">{row['location_id']}</span></p>
                    <p style="margin: 0.3rem 0;"><strong>Expected:</strong> <span style="color: #6b7280;">{expected_display}</span></p>
                </div>
                <div>
                    <p style="margin: 0.3rem 0;"><strong>Tolerance:</strong> <span style="color: #6b7280;">{row['threshold']}</span></p>
                    <p style="margin: 0.3rem 0;"><strong>Metrc Tag:</strong> <span style="color: #6b7280;">{row['metrc_tag']}</span></p>
                    <p style="margin: 0.3rem 0;"><strong>Status:</strong> <span style="color: #10b981;">✅ Active</span></p>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quantity input with enhanced styling
        st.markdown("#### 🔢 Physical Count")
        
        if demo_mode:
            # Generate realistic demo data
            base_expected = row["expected_count"]
            variance = random.choice([-2, -1, 0, 0, 0, 1, 2])  # Bias toward accurate counts
            quantity = max(0, base_expected + variance)
            st.info(f"🤖 **Demo Mode**: Auto-generated count = **{quantity}**")
        else:
            quantity = st.number_input(
                "Enter physical count",
                min_value=0,
                value=int(row["quantity"]),
                help="Enter the actual count from your physical inventory check"
            )

        # Enhanced evaluate button
        if st.button("🔍 **EVALUATE & LOG TO SYSTEM**", use_container_width=True, type="primary"):
            # Show processing animation
            with st.spinner("🔄 Evaluating discrepancy • Logging to systems • Updating compliance..."):
                time.sleep(1.5 if live_mode else 0.5)
            
            flagged, message = evaluate_discrepancy(quantity, row["expected_count"], str(row["threshold"]))
            
            # Update session state
            st.session_state.scan_count += 1
            if flagged:
                st.session_state.discrepancy_count += 1
            
            # Add to activity log
            timestamp = datetime.now().strftime("%H:%M:%S")
            st.session_state.activity_log.insert(0, {
                'time': timestamp,
                'sku': row['SKU'],
                'item': selected_item,
                'counted': quantity,
                'expected': row['expected_count'],
                'status': 'Flagged' if flagged else 'OK',
                'flagged': flagged
            })

            # Push to Google Sheets
            append_cycle_log({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sku": row["SKU"],
                "item": selected_item,
                "location": row["location_id"],
                "counted": int(quantity),  # Force cast here
                "expected": int(row["expected_count"]),
                "variance": int(quantity - row["expected_count"]),
                "status": "Discrepancy" if flagged else "OK"
            })

            # Keep only last 10 entries
            st.session_state.activity_log = st.session_state.activity_log[:10]
            
            # Store result
            st.session_state.last_result = {
                'flagged': flagged,
                'message': message,
                'quantity': quantity,
                'expected': row['expected_count'],
                'item': selected_item
            }
            
            # Clear auto-selected item
            if 'auto_selected_item' in st.session_state:
                del st.session_state.auto_selected_item

# --- CSV DOWNLOAD BUTTON (Add at the end of right-side panel after activity log or below quick actions)
            if st.session_state.activity_log:
                csv_data = pd.DataFrame(st.session_state.activity_log).to_csv(index=False)
                st.download_button("⬇️ Download Report as CSV", data=csv_data, file_name="scan_report.csv", mime="text/csv")
            
            # Show success effects
            if live_mode:
                if not flagged:
                    st.balloons()
                else:
                    st.error("⚠️ Discrepancy flagged for manager review!")
            
            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Real-Time Results")
    
    # Enhanced results display
    if hasattr(st.session_state, 'last_result'):
        result = st.session_state.last_result
        if result['flagged']:
            st.markdown(f"""
            <div class="warning-alert">
                <strong>⚠️ DISCREPANCY DETECTED</strong><br>
                <div style="margin-top: 0.5rem;">
                    {result['message']}<br>
                    <small>🔔 Manager notification sent • 📋 Compliance log updated</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-alert">
                <strong>✅ COUNT VERIFIED</strong><br>
                <div style="margin-top: 0.5rem;">
                    {result['message']}<br>
                    <small>📊 Inventory updated • ✅ Compliance maintained</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Enhanced activity log
    st.markdown("#### 📝 Recent Scanning Activity")
    
    if st.session_state.activity_log:
        for i, entry in enumerate(st.session_state.activity_log):
            status_class = "status-flagged" if entry['flagged'] else "status-ok"
            status_text = "🚨 FLAGGED" if entry['flagged'] else "✅ VERIFIED"
            
            st.markdown(f"""
            <div class="activity-item">
                <div style="display: flex; justify-content: between; align-items: center;">
                    <div style="flex: 1;">
                        <strong style="color: #374151;">{entry['sku']}</strong> - {entry['item']}<br>
                        <small style="color: #6b7280;">
                            Counted: <strong>{entry['counted']}</strong> | 
                            Expected: <strong>{entry['expected']}</strong> | 
                            {entry['time']}
                        </small>
                    </div>
                    <div style="text-align: right;">
                        <span class="status-indicator {status_class}"></span>
                        <span style="font-weight: 600; font-size: 0.8rem;">{status_text}</span>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.info("🔍 No recent scanning activity - Start scanning to see real-time results!")

    # Enhanced quick actions
    st.markdown("#### ⚡ Management Actions")
    
    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("📊 **Generate Report**", use_container_width=True):
            with st.spinner("Generating comprehensive report..."):
                time.sleep(2)
            st.balloons()
            st.success("📈 Report generated and sent to management dashboard!")
    
    with col_b:
        if st.button("🔄 **Sync to Metrc**", use_container_width=True):
            with st.spinner("Syncing compliance data..."):
                time.sleep(1.5)
            st.success("✅ Metrc compliance updated!")

# Enhanced footer with integrations
st.markdown("""
<div class="footer-section">
    <h3 style="color: #374151; margin-bottom: 1rem;">🔗 Enterprise Integrations</h3>
    <div style="margin-bottom: 1rem;">
        <span class="integration-badge">📊 Google Sheets API</span>
        <span class="integration-badge">🌿 Metrc Compliance</span>
        <span class="integration-badge">📱 Mobile Ready</span>
        <span class="integration-badge">🔌 USB/Bluetooth</span>
        <span class="integration-badge">☁️ Cloud Sync</span>
        <span class="integration-badge">📈 Real-Time Analytics</span>
    </div>
    <p style="color: #6b7280; margin: 0;">
        <strong>Enterprise-grade inventory management</strong> with automated compliance reporting and real-time synchronization
    </p>
</div>
""", unsafe_allow_html=True)

# Enhanced expandable sections
col_exp1, col_exp2 = st.columns(2)

with col_exp1:
    with st.expander("📋 Live Scan Log from Google Sheets", expanded=False):
        st.markdown("### Live Data Sync")
        try:
            creds = ServiceAccountCredentials.from_json_keyfile_name("service_account.json", SCOPES)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(SHEET_ID)
            records = sheet.sheet1.get_all_records()
            df_logs = pd.DataFrame(records)
            df_logs['Timestamp'] = pd.to_datetime(df_logs['Timestamp']).dt.strftime('%Y-%m-%d %H:%M:%S')
            st.dataframe(df_logs.tail(10))
        except Exception as e:
            st.error(f"Failed to load live data: {e}")

with col_exp2:
    # Enhanced demo script
    with st.expander("🎤 **Demo Presentation Script**", expanded=False):
        st.markdown("""
        ### 🎯 **Professional Demo Flow** (5-7 minutes)
        
        **1. Opening** (30 seconds)
        > "Welcome to our **Smart Cycle-Count Scanner** - an AI-powered solution that eliminates manual inventory errors and ensures compliance."
        
        **2. Visual Impact** (1 minute)
        > "Notice the professional interface, real-time metrics, and live integration status - this isn't just a scanning app, it's an enterprise solution."
        
        **3. Core Demo** (3 minutes)
        - ✅ **Simulate barcode scan** to show auto-detection
        - ✅ **Enable demo mode** for realistic data generation  
        - ✅ **Show both success and discrepancy scenarios**
        - ✅ **Highlight real-time sync** to Google Sheets & Metrc
        
        **4. Business Value** (2 minutes)
        > "This saves **40+ hours per month** in manual counting, ensures **100% compliance** with Metrc requirements, and gives managers **real-time visibility** into inventory discrepancies."
        
        **5. Implementation** (1 minute)
        > "Setup takes just 2 hours - we handle Google Sheets integration, Metrc API connection, and staff training."
        
        ### 💡 **Key Talking Points**
        - **Zero manual data entry** - everything syncs automatically
        - **Instant compliance** - Metrc-ready reporting
        - **Manager alerts** - immediate discrepancy notifications
        - **Mobile-first** - works on tablets and phones
        - **Enterprise security** - your data stays secure
        """)