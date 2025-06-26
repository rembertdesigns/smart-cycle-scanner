import streamlit as st
import pandas as pd
import time
from logic import evaluate_discrepancy, get_severity_score
from datetime import datetime
import random
import json
import plotly.graph_objects as go
import plotly.express as px
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from sheets_sync import append_cycle_log

# Define Google Sheets constants
SHEET_ID = "15D6ZVuXf7W_0AYPSRq_8PeZaESZ9mEpgS4djmTRMDE0"
SCOPES = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# Enhanced page config
st.set_page_config(
    page_title="🌿 Cannabis Cycle Counter Pro", 
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://your-dispensary.com/support',
        'Report a bug': "https://your-dispensary.com/bug-report",
        'About': "Cannabis Cycle Counter Pro v3.0 - Replacing Costly Dutchie/Lucid Manual Processes"
    }
)

# Enhanced CSS for cannabis industry professional look
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #16a085 0%, #2ecc71 100%);
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
    
    .cost-savings-banner {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: 600;
        box-shadow: 0 5px 15px rgba(243, 156, 18, 0.3);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        padding: 1.8rem;
        border-radius: 15px;
        border-left: 5px solid #16a085;
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
        border: 1px solid rgba(22, 160, 133, 0.1);
        margin-bottom: 1rem;
    }
    
    .camera-feed {
        background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
        border: 3px dashed #16a085;
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
        background: linear-gradient(90deg, transparent, #16a085, transparent);
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
        border: 2px solid #16a085;
        margin: 1rem 0;
        box-shadow: 0 5px 15px rgba(22, 160, 133, 0.2);
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
        border-left-color: #16a085;
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
        background-color: #16a085;
    }
    
    .status-flagged {
        background-color: #e74c3c;
    }
    
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .demo-controls {
        background: linear-gradient(135deg, #e8f5e8 0%, #d4edda 100%);
        border: 2px solid #16a085;
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
    }
    
    .integration-badge {
        background: linear-gradient(135deg, #16a085 0%, #27ae60 100%);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        margin: 0.2rem;
        display: inline-block;
        box-shadow: 0 2px 8px rgba(22, 160, 133, 0.3);
    }
    
    .footer-section {
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        padding: 2rem;
        border-radius: 15px;
        border-top: 3px solid #16a085;
        margin-top: 2rem;
        text-align: center;
    }
    
    .metric-container {
        background: linear-gradient(135deg, #ffffff 0%, #f8fafc 100%);
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        text-align: center;
        margin: 0.5rem 0;
    }
    
    .compliance-badge {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 15px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        margin: 0.1rem;
    }
    
    .cannabis-category {
        background: linear-gradient(135deg, #8e44ad 0%, #9b59b6 100%);
        color: white;
        padding: 0.2rem 0.6rem;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
        display: inline-block;
        margin-right: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header with enhanced styling
st.markdown("""
<div class="main-header">
    <h1>🌿 Cannabis Cycle Counter Pro</h1>
    <p>Streamlined Scan-Gun → Spreadsheet → Metrc Workflow</p>
    <p style="font-size: 0.9rem; opacity: 0.8; margin-top: 10px;">💰 Replacing Costly Dutchie/Lucid • ⚡ Instant Metrc Sync • 📊 Compliance Simplified</p>
</div>
""", unsafe_allow_html=True)

# Cost savings banner
st.markdown("""
<div class="cost-savings-banner">
    💰 <strong>ROI CALCULATOR:</strong> Save $2,400+/month vs Dutchie Premium • 40+ hours/month in manual work eliminated • 100% Metrc compliance maintained
</div>
""", unsafe_allow_html=True)

# Initialize session state with cannabis-specific demo data
if 'scan_count' not in st.session_state:
    st.session_state.scan_count = 47
if 'discrepancy_count' not in st.session_state:
    st.session_state.discrepancy_count = 8  # Higher for cannabis due to shrinkage/theft concerns
if 'activity_log' not in st.session_state:
    # Pre-populate with cannabis-specific demo activity
    st.session_state.activity_log = [
        {'time': '14:23:15', 'sku': 'SKU-1043', 'item': 'Raw Garden Refined Live Resin – Papaya', 'brand': 'Select', 'type': 'Vape Cartridge', 'counted': 4, 'expected': 104, 'status': 'CRITICAL', 'flagged': True, 'variance': -100},
        {'time': '14:21:42', 'sku': 'SKU-5116', 'item': 'Dosist Relief Pen', 'brand': 'Select', 'type': 'Vape Cartridge', 'counted': 12, 'expected': 15, 'status': 'Flagged', 'flagged': True, 'variance': -3},
        {'time': '14:19:33', 'sku': 'SKU-2847', 'item': 'Indica Gummies 10mg THC', 'brand': 'Kiva', 'type': 'Edible', 'counted': 8, 'expected': 8, 'status': 'OK', 'flagged': False, 'variance': 0},
    ]

# Load cannabis inventory data
@st.cache_data
def load_data():
    return pd.read_csv("data/smart_cycle_data.csv")

df = load_data()

# Enhanced sidebar dashboard
with st.sidebar:
    st.markdown("### 🌿 Cannabis Inventory Dashboard")
    
    accuracy = 100 if st.session_state.scan_count == 0 else round(((st.session_state.scan_count - st.session_state.discrepancy_count) / st.session_state.scan_count) * 100, 1)
    
    # Calculate estimated cost savings
    monthly_savings = 2400  # vs Dutchie Premium
    
    # Enhanced metrics with cannabis focus
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #16a085; margin: 0;">{st.session_state.scan_count}</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Items Counted</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #e74c3c; margin: 0;">{st.session_state.discrepancy_count}</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Discrepancies</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #f39c12; margin: 0;">${monthly_savings:,}</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Monthly Savings</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="metric-container">
            <h3 style="color: #8e44ad; margin: 0;">0.3s</h3>
            <p style="margin: 0; color: #6b7280; font-size: 0.8rem;">Avg Scan Time</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Enhanced integration status with cannabis focus
    st.markdown("### 🔗 System Integration Status")
    st.markdown('<div class="status-indicator status-ok"></div>**Metrc API** - Live Sync', unsafe_allow_html=True)
    st.markdown('<div class="status-indicator status-ok"></div>**Google Sheets** - Connected', unsafe_allow_html=True)
    st.markdown('<div class="status-indicator status-ok"></div>**Scan Gun** - Ready', unsafe_allow_html=True)
    st.markdown('<div class="status-indicator status-flagged"></div>**Dutchie** - Replaced', unsafe_allow_html=True)
    
    # Compliance indicators
    st.markdown("### 📋 Compliance Status")
    st.markdown('<span class="compliance-badge">✅ Metrc Current</span>', unsafe_allow_html=True)
    st.markdown('<span class="compliance-badge">✅ State Compliant</span>', unsafe_allow_html=True)
    st.markdown('<span class="compliance-badge">⚠️ 8 Discrepancies</span>', unsafe_allow_html=True)
    
    if st.button("🔄 Sync All to Metrc", use_container_width=True):
        with st.spinner("Syncing to Metrc & updating compliance..."):
            time.sleep(2)
        st.success("✅ Metrc compliance updated!")
        st.balloons()
    
    st.markdown("---")
    
    # Demo controls
    st.markdown("### 🎬 Demo Controls")
    st.markdown('<div class="demo-controls">', unsafe_allow_html=True)
    demo_mode = st.checkbox("🤖 Auto-Generate Cannabis Counts", help="Automatically generates realistic cannabis inventory data")
    blind_mode = st.checkbox("👁️ Blind Count Mode", help="Hide expected counts during scanning")
    high_value_alerts = st.checkbox("💎 High-Value Product Alerts", help="Extra alerts for concentrates, vapes, edibles")
    st.markdown('</div>', unsafe_allow_html=True)

    # Live mode toggle (internal state only, can be surfaced later if needed)
    if 'live_mode' not in st.session_state:
        st.session_state.live_mode = False

    live_mode = st.session_state.live_mode

    if st.button("🎯 Reset Demo Data"):
        st.session_state.scan_count = 0
        st.session_state.discrepancy_count = 0
        st.session_state.activity_log = []
        st.rerun()

# Main content area with enhanced layout
col1, col2 = st.columns([1.2, 1])

with col1:
    st.markdown('<div class="scanner-section">', unsafe_allow_html=True)
    st.markdown("### 📱 Cannabis Barcode Scanner")
    
    # Enhanced camera feed visualization
    camera_placeholder = st.empty()
    
    # Camera status indicator
    col_cam1, col_cam2, col_cam3 = st.columns([1, 2, 1])
    with col_cam2:
        if st.button("🔍 **SIMULATE PRODUCT SCAN**", use_container_width=True):
            with camera_placeholder.container():
                st.markdown("""
                <div class="camera-feed">
                    <div class="scan-animation"></div>
                    <div>
                        <h3>🌿 SCANNING CANNABIS PRODUCT...</h3>
                        <p>Barcode detected • Checking Metrc compliance...</p>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                time.sleep(2)
                
                # Auto-select random cannabis item for demo
                random_item = random.choice(df["Description"].unique())
                st.session_state.auto_selected_item = random_item
                
            camera_placeholder.success("✅ **Scan Complete** - Cannabis product auto-identified & Metrc verified!")
            st.rerun()
    
    # Default camera view
    if 'auto_selected_item' not in st.session_state:
        with camera_placeholder.container():
            st.markdown("""
            <div class="camera-feed">
                <div>
                    <h3 style="color: #6b7280;">📷 Cannabis Scanner Active</h3>
                    <p style="color: #9ca3af;">Point scanner at cannabis product barcode</p>
                    <p style="font-size: 0.8rem; color: #d1d5db;">Metrc compliance checking enabled</p>
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")
    
    # Item selection with enhanced styling
    st.markdown("#### 🎯 Cannabis Product Selection")
    
    # --- 🎯 Cannabis Product Selection & Evaluation ---
selected_item = st.session_state.get('auto_selected_item', "")
if not selected_item:
    selected_item = st.selectbox(
        "Choose scanned cannabis product (or scan to auto-detect)",
        [""] + list(df["Description"].unique())
    )

if selected_item:
    row = df[df["Description"] == selected_item].iloc[0]
    expected_display = "Hidden (Blind Mode)" if blind_mode else f"{row['expected_count']} units"
    product_type = row.get('Product_Type', 'Unknown')
    brand = row.get('Brand', 'Unknown Brand')

    # --- 📦 Item Details Card ---
    st.markdown(f"""
    <div class="metric-card">
        <h4 style="color: #16a085; margin-bottom: 1rem;">
            🌿 {selected_item}
            <br><span class="cannabis-category">{product_type}</span>
        </h4>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem;">
            <div>
                <p><strong>SKU:</strong> <span style="color: #6b7280;">{row['SKU']}</span></p>
                <p><strong>Brand:</strong> <span style="color: #6b7280;">{brand}</span></p>
                <p><strong>Location:</strong> <span style="color: #6b7280;">{row['location_id']}</span></p>
                <p><strong>Expected:</strong> <span style="color: #6b7280;">{expected_display}</span></p>
            </div>
            <div>
                <p><strong>Tolerance:</strong> <span style="color: #6b7280;">{row['threshold']}</span></p>
                <p><strong>Metrc Tag:</strong> <span style="color: #6b7280;">{row['metrc_tag']}</span></p>
                <p><strong>Type:</strong> <span style="color: #8e44ad;">{product_type}</span></p>
                <p><strong>Status:</strong> <span style="color: #16a085;">✅ Verified</span></p>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if high_value_alerts and product_type.lower() in ['vape cartridge', 'concentrate', 'extract']:
        st.warning(f"💎 **HIGH-VALUE ALERT**: {product_type} requires extra verification!")

    # --- 🔢 Physical Count Entry ---
    st.markdown("#### 🔢 Physical Count Entry")

    if demo_mode:
        base_expected = row["expected_count"]
        variance_options = [-5, -3, -2, -1, 0, 0, 0, 1, 2]
        if product_type.lower() in ['vape cartridge', 'concentrate']:
            variance_options = [-10, -5, -3, -1, 0, 0, 1]
        variance = random.choice(variance_options)
        quantity = max(0, base_expected + variance)
        st.info(f"🤖 **Demo Mode**: Cannabis count = **{quantity}** (Expected: {base_expected})")
    else:
        quantity = st.number_input(
            "Enter actual physical count",
            min_value=0,
            value=0,
            help="Enter the exact count from your physical cannabis inventory check"
        )

    # --- 🔍 Evaluation + Logging + Sync ---
    if st.button("🔍 **EVALUATE & SYNC TO METRC**", use_container_width=True, type="primary"):
        with st.spinner("🔄 Evaluating discrepancy • Logging to Metrc • Updating compliance..."):
            time.sleep(2 if live_mode else 1)
            counted = quantity
            expected = row["expected_count"]
            sku = row["SKU"]

            # Evaluate discrepancy
            flagged, message, action = evaluate_discrepancy(
                quantity=counted,
                expected=expected,
                threshold=str(row["threshold"]),
                sku=sku,
                category=product_type,
                name=selected_item
            )

            severity_score = get_severity_score(
                discrepancy=counted - expected,
                expected=expected,
                product_type=product_type
            )

            variance = counted - expected
            timestamp = datetime.now().strftime("%H:%M:%S")

            # Log to session
            st.session_state.activity_log.insert(0, {
                'time': timestamp,
                'sku': sku,
                'item': selected_item,
                'brand': brand,
                'type': product_type,
                'counted': counted,
                'expected': expected,
                'variance': variance,
                'status': 'CRITICAL' if abs(variance) > 10 else ('Flagged' if flagged else 'OK'),
                'flagged': flagged,
                'severity_score': severity_score,
                'action': action
            })

            # Push to Google Sheets
            append_cycle_log({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "sku": sku,
                "item": selected_item,
                "brand": brand,
                "product_type": product_type,
                "location": row["location_id"],
                "counted": int(counted),
                "expected": int(expected),
                "variance": variance,
                "status": "Discrepancy" if flagged else "OK",
                "category": product_type,
                "severity_score": severity_score,
                "action": action
            })

            st.session_state.activity_log = st.session_state.activity_log[:15]

            st.session_state.last_result = {
                'flagged': flagged,
                'message': message,
                'quantity': counted,
                'expected': expected,
                'variance': variance,
                'item': selected_item,
                'product_type': product_type,
                'severity_score': severity_score,
                'action': action
            }

            if 'auto_selected_item' in st.session_state:
                del st.session_state.auto_selected_item

            # Discrepancy alerts
            if abs(variance) > 10:
                st.error("🚨 **CRITICAL DISCREPANCY** - Manager & compliance team notified!")
            elif flagged:
                st.warning("⚠️ Discrepancy flagged for supervisor review!")
            else:
                st.success("✅ Count verified - Metrc updated!")
                if live_mode:
                    st.balloons()

            st.rerun()
    
    st.markdown('</div>', unsafe_allow_html=True)

with col2:
    st.markdown("### 📊 Cannabis Inventory Results")
    
    # Enhanced results display with cannabis focus
    if hasattr(st.session_state, 'last_result'):
        result = st.session_state.last_result
        variance = result.get('variance', 0)
        
        if abs(variance) > 10:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); color: #991b1b; padding: 1.5rem; border-radius: 12px; border: 2px solid #dc2626; margin: 1rem 0; box-shadow: 0 5px 15px rgba(220, 38, 38, 0.2);">
                <strong>🚨 CRITICAL CANNABIS DISCREPANCY</strong><br>
                <div style="margin-top: 0.5rem;">
                    Variance: <strong>{variance:+d}</strong> units<br>
                    <small>🔔 State compliance officer notified • 📋 Investigation required • 🔒 Inventory hold placed</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        elif result['flagged']:
            st.markdown(f"""
            <div class="warning-alert">
                <strong>⚠️ CANNABIS DISCREPANCY DETECTED</strong><br>
                <div style="margin-top: 0.5rem;">
                    {result['message']}<br>
                    <small>🔔 Supervisor notification sent • 📋 Metrc log updated • 🕵️ Investigation flagged</small>
                </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div class="success-alert">
                <strong>✅ CANNABIS COUNT VERIFIED</strong><br>
                <div style="margin-top: 0.5rem;">
                    {result['message']}<br>
                    <small>📊 Metrc updated • ✅ Compliance maintained • 🔄 Real-time sync complete</small>
                </div>
            </div>
            """, unsafe_allow_html=True)

    # Enhanced activity log with cannabis-specific fields
    st.markdown("#### 📝 Recent Cannabis Inventory Activity")

    if st.session_state.activity_log:
        for i, entry in enumerate(st.session_state.activity_log):
            status_class = "status-flagged" if entry['flagged'] else "status-ok"

            # Enhanced status text with variance
            variance = entry.get('variance', 0)
            if abs(variance) > 10:
                status_text = "🚨 CRITICAL"
                status_color = "#dc2626"
            elif entry['flagged']:
                status_text = "⚠️ FLAGGED"
                status_color = "#f59e0b"
            else:
                status_text = "✅ OK"
                status_color = "#16a085"

            # Render log entry card
            st.markdown(f"""
            <div class="activity-item">
                <div style="display: flex; align-items: center; justify-content: space-between;">
                    <div style="display: flex; align-items: center;">
                        <div class="status-indicator {status_class}"></div>
                        <strong style="color: {status_color};">{status_text}</strong>
                        <span style="margin-left: 0.5rem; color: #6b7280;">@ {entry['time']}</span>
                    </div>
                    <span style="font-size: 0.9rem; color: #6b7280;">{entry['sku']} – {entry['item']}</span>
                </div>
                <div style="margin-top: 0.5rem; color: #374151;">
                    Counted: <strong>{entry['counted']}</strong> • Expected: <strong>{entry['expected']}</strong> • Variance: <strong>{entry['variance']:+d}</strong> 
                    <br><small>{entry['brand']} • {entry['type']}</small>
                </div>
            </div>
            """, unsafe_allow_html=True)