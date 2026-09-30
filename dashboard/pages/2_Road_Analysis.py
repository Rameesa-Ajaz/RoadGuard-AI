"""
Road Analysis Page - Enhanced with Gauge, Routes, Turn-by-Turn
"""
import streamlit as st
import requests
import plotly.graph_objects as go
from datetime import datetime
import json

st.set_page_config(page_title="Road Analysis", page_icon="🔍")

st.title("🔍 Road Risk Analysis")

API_URL = "http://localhost:8000"

# Road selection with search
road_id = st.selectbox(
    "🛣️ Select Road Segment",
    [
        "Shahrah-e-Faisal, Karachi",
        "Korangi Road, Karachi",
        "Rashid Minhas Road, Karachi",
        "University Road, Karachi",
        "Mall Road, Lahore",
        "Ferozepur Road, Lahore",
        "GT Road, Punjab",
        "Murree Road, Rawalpindi",
        "Srinagar Highway, Islamabad",
        "Indus Highway, Sindh"
    ]
)

st.divider()

# Feature sliders in a nice grid
col1, col2, col3, col4 = st.columns(4)
with col1:
    infrastructure = st.slider("🏗️ Infrastructure", 0, 100, 35, help="Road surface, markings, lighting quality")
    traffic_flow = st.slider("🚗 Traffic Flow", 0, 5000, 1800, help="Vehicles per hour")
with col2:
    avg_speed = st.slider("💨 Avg Speed", 5, 120, 55, help="Average speed in km/h")
    signal_eff = st.slider("🚦 Signal Eff.", 0, 100, 45, help="Signal coordination efficiency")
with col3:
    divergence = st.slider("↔️ Divergence", 0, 100, 38, help="Lane change frequency")
    challan = st.slider("👮 Challan Ratio", 0, 100, 4, help="Enforcement presence")
with col4:
    root_eff = st.slider("📐 Root Eff.", 0, 100, 55, help="Road geometry management")
    accident_risk = st.slider("💥 Accident Risk", 0, 100, 72, help="Historical accident density")

if st.button("🔍 Analyze Road", type="primary", use_container_width=True):
    with st.spinner("🧠 AI models analyzing..."):
        payload = {
            "road_id": road_id,
            "city": road_id.split(",")[-1].strip(),
            "features": {
                "infrastructure_score": infrastructure,
                "traffic_flow": traffic_flow,
                "avg_speed": avg_speed,
                "signal_efficiency": signal_eff,
                "divergence_rate": divergence,
                "challan_ratio": challan,
                "root_efficiency": root_eff,
                "accident_risk": accident_risk
            }
        }

        try:
            resp = requests.post(f"{API_URL}/analyze", json=payload, timeout=10)

            if resp.status_code == 200:
                data = resp.json()
                risk_level = data['risk_level']
                risk_score = data['risk_score']

                # --- RISK GAUGE ---
                st.subheader("📊 Risk Assessment")

                gauge_color = "#10B981" if risk_level == 'low' else "#F59E0B" if risk_level == 'moderate' else "#F97316" if risk_level == 'high' else "#DC2626"

                col_g1, col_g2 = st.columns([1, 2])
                with col_g1:
                    fig_gauge = go.Figure(go.Indicator(
                        mode="gauge+number+delta",
                        value=risk_score,
                        domain={'x': [0, 1], 'y': [0, 1]},
                        title={'text': f"Risk Score<br><span style='font-size:16px;color:{gauge_color}'>{risk_level.upper()}</span>", 
                               'font': {'size': 20}},
                        delta={'reference': 50, 'increasing': {'color': "#DC2626"}},
                        gauge={
                            'axis': {'range': [None, 100], 'tickwidth': 2},
                            'bar': {'color': gauge_color, 'thickness': 0.75},
                            'bgcolor': "white",
                            'borderwidth': 3,
                            'bordercolor': "#E5E7EB",
                            'steps': [
                                {'range': [0, 20], 'color': '#D1FAE5'},
                                {'range': [20, 40], 'color': '#DBEAFE'},
                                {'range': [40, 60], 'color': '#FEF3C7'},
                                {'range': [60, 80], 'color': '#FFEDD5'},
                                {'range': [80, 100], 'color': '#FEE2E2'}
                            ],
                            'threshold': {
                                'line': {'color': "black", 'width': 4},
                                'thickness': 0.8,
                                'value': risk_score
                            }
                        }
                    ))
                    fig_gauge.update_layout(height=350, margin=dict(l=20, r=20, t=50, b=20))
                    st.plotly_chart(fig_gauge, use_container_width=True)

                with col_g2:
                    st.markdown("### 📈 Risk Trend (Simulated)")
                    import numpy as np
                    days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
                    trend = [risk_score + np.random.normal(0, 5) for _ in range(7)]
                    trend = [max(0, min(100, t)) for t in trend]

                    fig_trend = go.Figure()
                    fig_trend.add_trace(go.Scatter(
                        x=days, y=trend, mode='lines+markers',
                        line=dict(color=gauge_color, width=3),
                        marker=dict(size=10),
                        fill='tozeroy',
                        fillcolor=gauge_color.replace(')', ', 0.2)').replace('rgb', 'rgba') if 'rgb' in gauge_color else gauge_color + "33"
                    ))
                    fig_trend.update_layout(
                        height=300,
                        yaxis_range=[0, 100],
                        xaxis_title="Day",
                        yaxis_title="Risk Score",
                        showlegend=False
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)

                # --- FACTOR ATTRIBUTION ---
                st.subheader("🎯 Factor Attribution")

                factors = data['explanation'].get('attribution', '')
                st.info(factors)

                # Factor bars
                factor_data = {
                    'Infrastructure': 35 if infrastructure < 50 else 15,
                    'Divergence': 28 if divergence > 30 else 10,
                    'Challan Ratio': 20 if challan < 5 else 8,
                    'Traffic Flow': 10 if traffic_flow > 1500 else 5,
                    'Control': 7 if signal_eff < 50 else 3
                }

                fig_factors = go.Figure()
                colors = ['#DC2626' if v > 25 else '#F59E0B' if v > 15 else '#3B82F6' for v in factor_data.values()]
                fig_factors.add_trace(go.Bar(
                    x=list(factor_data.keys()),
                    y=list(factor_data.values()),
                    marker_color=colors,
                    text=[f"{v}%" for v in factor_data.values()],
                    textposition='auto'
                ))
                fig_factors.update_layout(
                    title="Risk Factor Contributions",
                    yaxis_title="Contribution (%)",
                    height=300,
                    showlegend=False
                )
                st.plotly_chart(fig_factors, use_container_width=True)

                # --- CAUSAL CHAIN ---
                st.subheader("🔗 Causal Chain Analysis")
                st.markdown(data['explanation'].get('causal_chain', 'No causal chain available.'))

                # --- COUNTERFACTUAL ---
                st.subheader("💭 Counterfactual: What If?")
                st.markdown(data['explanation'].get('counterfactual', 'No counterfactual available.'))

                # --- RECOMMENDATIONS ---
                st.subheader("💡 AI Recommendations")
                recs = data['recommendations']

                alert_color = recs.get('alert_color', 'gray')
                color_map = {'red': '#FEE2E2', 'orange': '#FEF3C7', 'yellow': '#FEF9C3', 'green': '#D1FAE5'}
                border_map = {'red': '#DC2626', 'orange': '#F59E0B', 'yellow': '#EAB308', 'green': '#10B981'}

                st.markdown(f"""
                <div style="background-color: {color_map.get(alert_color, '#F3F4F6')}; 
                            border-left: 5px solid {border_map.get(alert_color, '#6B7280')};
                            padding: 20px; border-radius: 10px; margin: 10px 0;">
                    <h4 style="margin: 0 0 10px 0; color: {border_map.get(alert_color, '#374151')};">
                        Priority {recs['priority']}: {recs['action_type']}
                    </h4>
                    <p style="margin: 5px 0;"><b>Alert Level:</b> {recs['alert_level']}%</p>
                    <p style="margin: 5px 0;"><b>Expected Impact:</b> {recs.get('estimated_impact', 'N/A')}</p>
                    <ul style="margin: 10px 0;">
                """, unsafe_allow_html=True)

                for action in recs['recommended_actions']:
                    st.markdown(f"<li>{action}</li>", unsafe_allow_html=True)

                st.markdown("</ul></div>", unsafe_allow_html=True)

                # --- ALTERNATIVE ROUTES ---
                st.subheader("🗺️ Alternative Routes")
                routes = data['alternative_routes']

                cols = st.columns(3)
                route_configs = [
                    ("🏃 Fastest", "fastest", "#DC2626"),
                    ("⚖️ Balanced", "balanced", "#F59E0B"),
                    ("🛡️ Safest", "safest", "#10B981")
                ]

                for col, (label, key, color) in zip(cols, route_configs):
                    route = routes.get(key, {})
                    with col:
                        st.markdown(f"""
                        <div style="border: 3px solid {color}; border-radius: 15px; padding: 20px; 
                                    background: linear-gradient(135deg, {color}11, {color}05);">
                            <h3 style="margin: 0; color: {color};">{label}</h3>
                            <p style="font-size: 24px; margin: 10px 0; font-weight: bold;">
                                ⏱️ {route.get('time_min', 'N/A')} min
                            </p>
                            <p style="font-size: 18px; margin: 5px 0;">
                                📏 {route.get('distance_km', 'N/A')} km
                            </p>
                            <p style="font-size: 20px; margin: 5px 0; color: {color}; font-weight: bold;">
                                ⚠️ Risk: {route.get('risk_score', 'N/A')}%
                            </p>
                            <p style="font-size: 14px; color: #666; margin: 10px 0;">
                                {route.get('description', '')}
                            </p>
                        </div>
                        """, unsafe_allow_html=True)

                        if key == 'safest':
                            st.success("✅ RECOMMENDED")
                        elif key == 'fastest':
                            st.error("🔴 Highest Risk")
                        else:
                            st.info("🟡 Moderate Option")

                # --- TURN-BY-TURN DIRECTIONS ---
                st.subheader("📍 Turn-by-Turn Directions (Safest Route)")

                directions = [
                    {"step": 1, "instruction": f"Start on {road_id.split(',')[0]} → Head South", "risk": "low", "dist": "0 km"},
                    {"step": 2, "instruction": "Continue straight on Service Road (low risk zone)", "risk": "low", "dist": "2.3 km"},
                    {"step": 3, "instruction": "At 5.1 km, take left at signal (moderate risk)", "risk": "moderate", "dist": "5.1 km"},
                    {"step": 4, "instruction": "Merge onto Korangi Road (watch for divergence)", "risk": "moderate", "dist": "8.7 km"},
                    {"step": 5, "instruction": "Arrive at destination", "risk": "low", "dist": "18 km"},
                ]

                for d in directions:
                    risk_emoji = {"low": "🟢", "moderate": "🟡", "high": "🟠", "critical": "🔴"}
                    st.markdown(f"""
                    <div style="display: flex; align-items: center; padding: 15px; 
                                background: #F9FAFB; border-radius: 10px; margin: 8px 0;
                                border-left: 4px solid {'#10B981' if d['risk']=='low' else '#F59E0B'};">
                        <div style="font-size: 24px; font-weight: bold; margin-right: 20px; color: #6B7280;">
                            {d['step']}
                        </div>
                        <div style="flex: 1;">
                            <div style="font-weight: 500;">{d['instruction']}</div>
                            <div style="font-size: 12px; color: #9CA3AF; margin-top: 4px;">
                                {risk_emoji.get(d['risk'], '⚪')} {d['risk'].title()} Risk | 📍 {d['dist']}
                            </div>
                        </div>
                    </div>
                    """, unsafe_allow_html=True)

                # Action buttons
                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1:
                    st.button("📱 Send to Phone", use_container_width=True)
                with col_b2:
                    st.button("🖨️ Print Route", use_container_width=True)
                with col_b3:
                    if st.button("📋 Export Report", use_container_width=True):
                        report = {
                            "road_id": road_id,
                            "timestamp": datetime.now().isoformat(),
                            "risk_score": risk_score,
                            "risk_level": risk_level,
                            "features": payload["features"],
                            "recommendations": recs,
                            "explanation": data["explanation"]
                        }
                        st.download_button(
                            "⬇️ Download JSON",
                            json.dumps(report, indent=2),
                            file_name=f"road_analysis_{road_id.replace(' ', '_').replace(',', '')}.json",
                            mime="application/json"
                        )

            elif resp.status_code == 503:
                st.error("⚠️ Model not trained. Run: `python scripts/run_pipeline.py` first, then restart the API.")
            else:
                st.error(f"API Error {resp.status_code}: {resp.text}")

        except requests.exceptions.ConnectionError:
            st.error("❌ Cannot connect to API at localhost:8000. Please start the backend: `uvicorn src.api.main:app --reload`")
        except Exception as e:
            st.error(f"Error: {e}")
