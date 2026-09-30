"""
Dashboard Overview Page - Enhanced with Filters & Time Controls
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Overview", page_icon="📊", layout="wide")

st.title("📊 System Overview")

# --- SIDEBAR FILTERS ---
with st.sidebar:
    st.header("🎛️ Filters & Controls")

    # Time range slider
    st.subheader("⏰ Time Window")
    time_options = ["Last 24 Hours", "Last 7 Days", "Last 30 Days", "Last 90 Days", "2026 YTD"]
    time_range = st.selectbox("Select Period", time_options, index=1)

    # Province filter
    st.subheader("🗺️ Geography")
    provinces = st.multiselect(
        "Provinces",
        ["Punjab", "Sindh", "KPK", "Balochistan", "Islamabad"],
        default=["Punjab", "Sindh", "KPK", "Balochistan", "Islamabad"]
    )

    # City filter
    cities = st.multiselect(
        "Cities",
        ["Karachi", "Lahore", "Islamabad", "Rawalpindi", "Peshawar", "Quetta", "Hyderabad"],
        default=["Karachi", "Lahore", "Islamabad"]
    )

    # Risk level filter
    st.subheader("⚠️ Risk Levels")
    risk_levels = st.multiselect(
        "Show Levels",
        ["Critical", "High", "Moderate", "Low"],
        default=["Critical", "High", "Moderate", "Low"]
    )

    # Road type filter
    st.subheader("🛣️ Road Types")
    road_types = st.multiselect(
        "Road Types",
        ["Highway", "Arterial", "Local", "Residential"],
        default=["Highway", "Arterial", "Local"]
    )

    st.divider()

    # Auto refresh
    auto_refresh = st.toggle("🔄 Auto Refresh", value=False)
    if auto_refresh:
        st.caption("Refreshing every 60s")

    st.divider()
    st.info(f"📅 Last Updated: {datetime.now().strftime('%H:%M:%S')}")

# --- KPI CARDS ---
st.subheader("📈 Key Performance Indicators")

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    st.metric("🚨 Critical Risk", "23", "↑ 12%", delta_color="inverse")
with col2:
    st.metric("⚠️ High Risk", "45", "↓ 3%", delta_color="inverse")
with col3:
    st.metric("📊 Total Roads", "250", "")
with col4:
    st.metric("📉 Recent Accidents", "12", "↓ 5%", delta_color="inverse")
with col5:
    st.metric("🛡️ Avg Risk Score", "48.3", "↓ 2.1%", delta_color="inverse")

st.divider()

# --- RISK TREND WITH TIME SLIDER ---
st.subheader("📊 Risk Trend Over Time")

# Generate trend data based on selected time range
days_map = {"Last 24 Hours": 1, "Last 7 Days": 7, "Last 30 Days": 30, "Last 90 Days": 90, "2026 YTD": 220}
n_days = days_map.get(time_range, 7)

dates = pd.date_range(end=datetime.now(), periods=n_days, freq='D')
np.random.seed(42)

# Simulate realistic trend data
trend_data = pd.DataFrame({
    'Date': dates,
    'Critical': [20 + np.random.randint(-3, 5) for _ in range(n_days)],
    'High': [45 + np.random.randint(-5, 8) for _ in range(n_days)],
    'Moderate': [78 + np.random.randint(-8, 5) for _ in range(n_days)],
    'Low': [104 + np.random.randint(-5, 8) for _ in range(n_days)],
    'Avg_Risk': [48 + np.random.normal(0, 3) for _ in range(n_days)]
})

# Time slider for detailed view
if n_days > 7:
    date_range = st.slider(
        "Select Date Range",
        min_value=dates[0].date(),
        max_value=dates[-1].date(),
        value=(dates[max(0, n_days-14)].date(), dates[-1].date())
    )
    mask = (trend_data['Date'].dt.date >= date_range[0]) & (trend_data['Date'].dt.date <= date_range[1])
    filtered_trend = trend_data[mask]
else:
    filtered_trend = trend_data

fig_trend = go.Figure()
for col, color in [('Critical', '#DC2626'), ('High', '#F97316'), ('Moderate', '#F59E0B'), ('Low', '#10B981')]:
    if col in risk_levels:
        fig_trend.add_trace(go.Scatter(
            x=filtered_trend['Date'], y=filtered_trend[col],
            mode='lines', name=col, line=dict(color=color, width=2),
            fill='tonexty' if col != 'Critical' else 'none'
        ))

fig_trend.update_layout(
    title=f"Risk Level Distribution - {time_range}",
    height=400,
    xaxis_title="Date",
    yaxis_title="Number of Roads",
    legend=dict(orientation="h", yanchor="bottom", y=1.02),
    hovermode='x unified'
)
st.plotly_chart(fig_trend, use_container_width=True)

st.divider()

# --- CHARTS ROW ---
col_left, col_right = st.columns(2)

with col_left:
    st.subheader("📊 Risk Distribution")
    data = {'Level': ['Critical', 'High', 'Moderate', 'Low'], 'Count': [23, 45, 78, 104]}
    fig = px.bar(data, x='Level', y='Count', color='Level',
                 color_discrete_map={'Critical':'#dc2626', 'High':'#f59e0b', 
                                    'Moderate':'#3b82f6', 'Low':'#10b981'},
                 text='Count')
    fig.update_traces(textposition='outside')
    fig.update_layout(height=350, showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.subheader("🏆 Top Risk Factors")
    factors = {'Infrastructure': 35, 'Divergence': 28, 'Challan Ratio': 20, 'Flow': 10, 'Control': 7}
    fig = px.pie(values=list(factors.values()), names=list(factors.keys()),
                 hole=0.4, title="Factor Contribution")
    fig.update_traces(textinfo='percent+label', textfont_size=12)
    fig.update_layout(height=350)
    st.plotly_chart(fig, use_container_width=True)

st.divider()

# --- PROVINCIAL COMPARISON ---
st.subheader("🏙️ Provincial Accident Overview")

province_data = pd.DataFrame({
    'Province': ['Punjab', 'Sindh', 'KPK', 'Balochistan', 'ICT'],
    'Accidents': [1560000, 700000, 314000, 111245, 80000],
    'Fatalities': [18001, 12286, 7545, 5969, 3200],
    'Fatality_Rate': [1.15, 1.75, 2.40, 5.36, 4.00]
})

# Filter by selected provinces
province_data = province_data[province_data['Province'].isin(provinces)]

fig_prov = px.bar(province_data, x='Province', y=['Accidents', 'Fatalities'],
                  barmode='group', title="Accidents vs Fatalities by Province",
                  color_discrete_map={'Accidents': '#3B82F6', 'Fatalities': '#DC2626'})
fig_prov.update_layout(height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02))
st.plotly_chart(fig_prov, use_container_width=True)

st.divider()

# --- RECENT ALERTS ---
st.subheader("🔔 Recent Alerts (Last 60 Minutes)")

alerts = [
    {"time": "14:45", "level": "🔴 CRITICAL", "road": "Shahrah-e-Faisal, Karachi", 
     "detail": "High divergence (52 veh/min) | Risk: 92%", "color": "#FEE2E2"},
    {"time": "14:30", "level": "🟠 HIGH", "road": "Mall Road, Lahore",
     "detail": "Traffic flow > 85% capacity | Risk: 72%", "color": "#FEF3C7"},
    {"time": "14:20", "level": "🟠 HIGH", "road": "GT Road, Punjab",
     "detail": "Speeding violations (72% overspeeding) | Risk: 68%", "color": "#FEF3C7"},
    {"time": "14:15", "level": "🟡 MODERATE", "road": "Murree Road, Rawalpindi",
     "detail": "Poor signal timing | Risk: 48%", "color": "#FEF9C3"},
    {"time": "14:05", "level": "🟢 LOW", "road": "Srinagar Highway, Islamabad",
     "detail": "Normal conditions | Risk: 22%", "color": "#D1FAE5"},
]

for alert in alerts:
    st.markdown(f"""
    <div style="background-color: {alert['color']}; padding: 15px; border-radius: 10px; 
                margin: 8px 0; border-left: 4px solid {'#DC2626' if 'CRITICAL' in alert['level'] else '#F59E0B' if 'HIGH' in alert['level'] else '#10B981'};">
        <div style="display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-weight: bold; font-size: 16px;">{alert['level']}</span>
                <span style="color: #6B7280; margin-left: 10px;">⏰ {alert['time']}</span>
            </div>
        </div>
        <div style="margin-top: 8px; font-weight: 500;">📍 {alert['road']}</div>
        <div style="margin-top: 4px; color: #4B5563; font-size: 14px;">{alert['detail']}</div>
    </div>
    """, unsafe_allow_html=True)

st.divider()

# --- EXPORT SECTION ---
st.subheader("📤 Export Dashboard Data")

col_e1, col_e2 = st.columns(2)
with col_e1:
    if st.button("📊 Export as CSV", use_container_width=True):
        export_df = pd.DataFrame({
            'Metric': ['Critical Roads', 'High Risk Roads', 'Moderate Roads', 'Low Risk Roads', 
                      'Total Accidents (3mo)', 'Avg Risk Score'],
            'Value': [23, 45, 78, 104, 12, 48.3],
            'Province': ['All', 'All', 'All', 'All', 'All', 'All']
        })
        st.download_button(
            "⬇️ Download CSV",
            export_df.to_csv(index=False),
            file_name=f"traffic_dashboard_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

with col_e2:
    if st.button("📈 Export as PDF Report", use_container_width=True):
        st.info("📄 PDF export feature requires additional setup. Use the API `/export/report` endpoint for programmatic PDF generation.")

st.caption(f"🚦 Smart Traffic Risk System | Pakistan | v1.0.0 | {datetime.now().strftime('%Y-%m-%d %H:%M')}")
