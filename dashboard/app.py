"""
Streamlit Dashboard - Main Application (Multi-page entry point).
Enhanced with mobile responsive design, export functionality, and rich navigation.
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import requests

# Page config
st.set_page_config(
    page_title="Traffic Risk System - Pakistan",
    page_icon="🚦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS - Desktop + Mobile responsive
st.markdown("""
<style>
    /* Main header */
    .main-header { 
        font-size: 2.5rem; 
        font-weight: bold; 
        color: #1e3a8a; 
        margin-bottom: 0.5rem;
    }

    /* Risk cards */
    .risk-critical { 
        background-color: #fee2e2; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        border-left: 4px solid #dc2626;
        margin: 0.5rem 0;
    }
    .risk-high { 
        background-color: #fef3c7; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        border-left: 4px solid #f59e0b;
        margin: 0.5rem 0;
    }
    .risk-moderate { 
        background-color: #dbeafe; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        border-left: 4px solid #3b82f6;
        margin: 0.5rem 0;
    }
    .risk-low { 
        background-color: #d1fae5; 
        padding: 1rem; 
        border-radius: 0.5rem; 
        border-left: 4px solid #10b981;
        margin: 0.5rem 0;
    }

    /* Mobile bottom navigation */
    @media (max-width: 768px) {
        .main-header { font-size: 1.5rem !important; }
        .stSidebar { display: none !important; }
        .mobile-nav {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background: #1e3a8a;
            display: flex;
            justify-content: space-around;
            padding: 10px 0;
            z-index: 9999;
            border-top: 2px solid #3b82f6;
        }
        .mobile-nav a {
            color: white;
            text-decoration: none;
            font-size: 12px;
            text-align: center;
            flex: 1;
        }
        .mobile-nav a:hover {
            color: #fbbf24;
        }
        .main .block-container {
            padding-bottom: 80px !important;
        }
    }

    /* Desktop sidebar styling */
    @media (min-width: 769px) {
        .mobile-nav { display: none !important; }
    }

    /* Metric cards */
    div[data-testid="stMetricValue"] {
        font-size: 28px !important;
        font-weight: bold !important;
    }

    /* Buttons */
    .stButton>button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    .stButton>button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    }

    /* Cards */
    .stAlert {
        border-radius: 10px !important;
    }

    /* Tables */
    .stDataFrame {
        border-radius: 10px;
        overflow: hidden;
    }
</style>
""", unsafe_allow_html=True)

# Mobile bottom navigation (shown only on mobile via CSS)
st.markdown("""
<div class="mobile-nav">
    <a href="/Overview" target="_self">📊<br>Overview</a>
    <a href="/Road_Analysis" target="_self">🔍<br>Analysis</a>
    <a href="/Map" target="_self">🗺️<br>Map</a>
    <a href="/Explanations" target="_self">🧠<br>Insights</a>
    <a href="/System_Monitor" target="_self">🔧<br>Monitor</a>
</div>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🚦 Smart Traffic Risk System - Pakistan</h1>', unsafe_allow_html=True)
st.caption(f"🟢 System Operational | Last Updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} PKT")

# Sidebar navigation
with st.sidebar:
    st.header("📍 Navigation")
    st.info("""
    Use the pages above for detailed views:
    - **Overview**: System-wide summary
    - **Road Analysis**: AI-powered risk analysis
    - **Map**: Interactive risk map
    - **Explanations**: Analytics & insights
    - **System Monitor**: Real-time status
    """)

    st.divider()
    st.header("🔧 Quick Actions")

    if st.button("🔄 Refresh Data", use_container_width=True):
        st.rerun()

    if st.button("📤 Export Summary", use_container_width=True):
        summary_data = {
            "timestamp": datetime.now().isoformat(),
            "critical_risk": 23,
            "high_risk": 45,
            "moderate_risk": 78,
            "low_risk": 104,
            "total_roads": 250,
            "recent_accidents": 12,
            "avg_risk_score": 48.3
        }
        st.download_button(
            "⬇️ Download JSON",
            pd.Series(summary_data).to_json(),
            file_name=f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
            mime="application/json"
        )

    st.divider()
    st.header("📊 System Stats")
    st.metric("🚨 Critical", "23", "↑ 3%")
    st.metric("⚠️ High", "45", "↓ 2%")
    st.metric("📊 Total Roads", "250")

    st.divider()
    st.caption("v1.0.0 | © 2026 Pakistan Traffic AI")

# Main content
st.info("""
👋 **Welcome!** This is the main entry point. Use the sidebar or the page navigation 
at the top to access different views. On mobile, use the bottom navigation bar.
""")

# KPI Cards
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("🚨 Critical Risk", "23", "↑ 3", delta_color="inverse")
with col2:
    st.metric("⚠️ High Risk", "45", "↓ 2", delta_color="inverse")
with col3:
    st.metric("📊 Total Roads", "250", "")
with col4:
    st.metric("📅 Recent Accidents", "12", "↓ 5", delta_color="inverse")

st.divider()

# Charts
st.subheader("📊 Quick Overview")

col1, col2 = st.columns(2)
with col1:
    st.subheader("Risk Distribution")
    data = {'Level': ['Critical', 'High', 'Moderate', 'Low'], 'Count': [23, 45, 78, 104]}
    fig = px.bar(data, x='Level', y='Count', color='Level',
                 color_discrete_map={'Critical':'#dc2626', 'High':'#f59e0b', 
                                    'Moderate':'#3b82f6', 'Low':'#10b981'},
                 text='Count')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    st.subheader("Top Risk Factors")
    factors = {'Infrastructure': 35, 'Divergence': 28, 'Challan Ratio': 20, 'Flow': 10, 'Control': 7}
    fig = px.pie(values=list(factors.values()), names=list(factors.keys()), 
                 hole=0.4, title="Factor Contributions")
    fig.update_traces(textinfo='percent+label', textfont_size=12)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# Provincial data
st.subheader("🇵🇰 Provincial Accident Overview")
province_data = pd.DataFrame({
    'Province': ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'ICT'],
    'Accidents': [1560000, 700000, 314000, 111245, 80000],
    'Fatalities': [18001, 12286, 7545, 5969, 3200]
})
fig = px.bar(province_data, x='Province', y=['Accidents', 'Fatalities'],
             barmode='group', title="Accidents vs Fatalities by Province",
             color_discrete_map={'Accidents': '#3B82F6', 'Fatalities': '#DC2626'})
fig.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig, use_container_width=True)

st.divider()

# Vehicle involvement
st.subheader("🏍️ Key Statistics - Pakistan Road Safety (2019-2024)")

col_s1, col_s2, col_s3 = st.columns(3)
with col_s1:
    st.markdown("""
    ### 🏍️ Vehicle Involvement
    - **Motorcycles**: 71% of fatal accidents
    - **Cars**: 23%
    - **Buses/Trucks**: 14%
    - **Others**: 8%
    """)
with col_s2:
    st.markdown("""
    ### ⚠️ Primary Causes
    1. Speeding: **37%**
    2. Unlicensed drivers: **35%**
    3. Poor Infrastructure: **30%**
    4. Distracted driving: 22%
    5. Weather conditions: 15%
    """)
with col_s3:
    st.markdown("""
    ### 💰 E-Challan Impact
    - **Karachi**: 164K challans (Mar 2026)
    - **Islamabad**: 65K (2025)
    - Helmet compliance: **96%**
    - Fatal accidents: **↓45%**
    - Licensed drivers: **37% → 81%**
    """)

st.divider()

# Footer
st.caption("🚦 Smart Traffic Risk System - Pakistan | AI-Powered Road Safety | v1.0.0")
