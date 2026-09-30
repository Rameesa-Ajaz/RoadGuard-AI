"""
Interactive Risk Map - Pakistan Roads
"""
import streamlit as st
import folium
from folium.plugins import HeatMap, MarkerCluster
from streamlit_folium import st_folium
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(page_title="Risk Map", page_icon="🗺️", layout="wide")

st.title("🗺️ Interactive Risk Map - Pakistan")
st.caption(f"Updated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")

# Sidebar filters
with st.sidebar:
    st.header("🎛️ Map Filters")
    province_filter = st.multiselect(
        "Province",
        ["All", "Punjab", "Sindh", "KPK", "Balochistan", "Islamabad"],
        default=["All"]
    )
    risk_filter = st.multiselect(
        "Risk Level",
        ["Critical", "High", "Moderate", "Low"],
        default=["Critical", "High", "Moderate", "Low"]
    )
    show_heatmap = st.toggle("Show Heatmap Layer", value=True)
    show_markers = st.toggle("Show Road Markers", value=True)

    st.divider()
    st.info("💡 Click any road marker for detailed analysis. Zoom in for better detail.")

# Generate realistic Pakistan road data with coordinates
@st.cache_data
def get_road_data():
    roads = [
        {"name": "Shahrah-e-Faisal", "city": "Karachi", "province": "Sindh", 
         "lat": 24.8607, "lon": 67.0011, "risk": 92, "level": "Critical",
         "accidents_3m": 12, "length_km": 14.5},
        {"name": "Korangi Road", "city": "Karachi", "province": "Sindh",
         "lat": 24.8400, "lon": 67.1300, "risk": 78, "level": "High",
         "accidents_3m": 8, "length_km": 10.2},
        {"name": "Rashid Minhas Road", "city": "Karachi", "province": "Sindh",
         "lat": 24.9200, "lon": 67.0800, "risk": 65, "level": "High",
         "accidents_3m": 5, "length_km": 8.5},
        {"name": "University Road", "city": "Karachi", "province": "Sindh",
         "lat": 24.9400, "lon": 67.1100, "risk": 58, "level": "Moderate",
         "accidents_3m": 3, "length_km": 7.0},
        {"name": "Mall Road", "city": "Lahore", "province": "Punjab",
         "lat": 31.5204, "lon": 74.3587, "risk": 72, "level": "High",
         "accidents_3m": 9, "length_km": 6.5},
        {"name": "Ferozepur Road", "city": "Lahore", "province": "Punjab",
         "lat": 31.4800, "lon": 74.3200, "risk": 68, "level": "High",
         "accidents_3m": 7, "length_km": 12.0},
        {"name": "GT Road (Lahore)", "city": "Lahore", "province": "Punjab",
         "lat": 31.5500, "lon": 74.2800, "risk": 55, "level": "Moderate",
         "accidents_3m": 4, "length_km": 18.0},
        {"name": "Murree Road", "city": "Rawalpindi", "province": "Punjab",
         "lat": 33.6844, "lon": 73.0479, "risk": 48, "level": "Moderate",
         "accidents_3m": 3, "length_km": 15.0},
        {"name": "Srinagar Highway", "city": "Islamabad", "province": "Islamabad",
         "lat": 33.7295, "lon": 73.0372, "risk": 35, "level": "Low",
         "accidents_3m": 1, "length_km": 20.0},
        {"name": "Indus Highway", "city": "Hyderabad", "province": "Sindh",
         "lat": 25.3960, "lon": 68.3578, "risk": 81, "level": "High",
         "accidents_3m": 10, "length_km": 25.0},
        {"name": "RCD Highway", "city": "Quetta", "province": "Balochistan",
         "lat": 30.1798, "lon": 66.9750, "risk": 74, "level": "High",
         "accidents_3m": 6, "length_km": 30.0},
        {"name": "Peshawar Road", "city": "Peshawar", "province": "KPK",
         "lat": 34.0151, "lon": 71.5249, "risk": 62, "level": "Moderate",
         "accidents_3m": 4, "length_km": 9.0},
    ]
    return pd.DataFrame(roads)

df = get_road_data()

# Apply filters
if "All" not in province_filter:
    df = df[df["province"].isin(province_filter)]
df = df[df["level"].isin(risk_filter)]

# Color mapping
risk_colors = {
    "Critical": "#DC2626",
    "High": "#F97316",
    "Moderate": "#F59E0B",
    "Low": "#10B981"
}

# Create map centered on Pakistan
center_lat, center_lon = 30.3753, 69.3451
m = folium.Map(location=[center_lat, center_lon], zoom_start=6, 
               tiles="CartoDB positron")

# Add heatmap layer
if show_heatmap and len(df) > 0:
    heat_data = [[row["lat"], row["lon"], row["risk"]/100] for _, row in df.iterrows()]
    HeatMap(heat_data, radius=25, blur=15, max_zoom=10).add_to(m)

# Add markers
if show_markers and len(df) > 0:
    marker_cluster = MarkerCluster(name="Road Segments").add_to(m)
    for _, row in df.iterrows():
        color = risk_colors.get(row["level"], "gray")
        popup_html = f"""
        <div style="font-family: Arial; min-width: 200px;">
            <h4 style="margin: 0; color: {color};">🚦 {row["name"]}</h4>
            <p style="margin: 5px 0;"><b>City:</b> {row["city"]}</p>
            <p style="margin: 5px 0;"><b>Province:</b> {row["province"]}</p>
            <p style="margin: 5px 0;"><b>Risk Score:</b> {row["risk"]}%</p>
            <p style="margin: 5px 0;"><b>Level:</b> <span style="color: {color}; font-weight: bold;">{row["level"]}</span></p>
            <p style="margin: 5px 0;"><b>Accidents (3mo):</b> {row["accidents_3m"]}</p>
            <p style="margin: 5px 0;"><b>Length:</b> {row["length_km"]} km</p>
            <hr style="margin: 10px 0;">
            <a href="/Road_Analysis" target="_blank" style="color: #1E3A8A; font-weight: bold;">🔍 Analyze This Road</a>
        </div>
        """
        folium.CircleMarker(
            location=[row["lat"], row["lon"]],
            radius=8 + row["risk"] / 15,
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=f"{row['name']} - {row['risk']}%",
            color=color,
            fill=True,
            fillColor=color,
            fillOpacity=0.7,
            weight=2
        ).add_to(marker_cluster)

# Add legend
legend_html = """
<div style="position: fixed; 
            bottom: 50px; left: 50px; width: 180px; 
            background-color: white; border: 2px solid #ddd; 
            border-radius: 10px; padding: 15px; z-index: 9999;
            font-family: Arial; box-shadow: 2px 2px 10px rgba(0,0,0,0.2);">
    <h4 style="margin: 0 0 10px 0;">🎨 Risk Legend</h4>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="width: 20px; height: 20px; background: #DC2626; border-radius: 50%; margin-right: 10px;"></span>
        <span>Critical (80-100)</span>
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="width: 20px; height: 20px; background: #F97316; border-radius: 50%; margin-right: 10px;"></span>
        <span>High (60-79)</span>
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="width: 20px; height: 20px; background: #F59E0B; border-radius: 50%; margin-right: 10px;"></span>
        <span>Moderate (40-59)</span>
    </div>
    <div style="display: flex; align-items: center; margin: 5px 0;">
        <span style="width: 20px; height: 20px; background: #10B981; border-radius: 50%; margin-right: 10px;"></span>
        <span>Low (0-39)</span>
    </div>
</div>
"""
m.get_root().html.add_child(folium.Element(legend_html))

# Display map
col1, col2 = st.columns([3, 1])
with col1:
    st_folium(m, width=900, height=600, returned_objects=[])

with col2:
    st.subheader("📍 Road List")
    st.dataframe(
        df[["name", "city", "risk", "level"]].sort_values("risk", ascending=False),
        use_container_width=True,
        hide_index=True
    )

    st.divider()
    st.subheader("📊 Quick Stats")
    st.metric("Roads Shown", len(df))
    st.metric("Avg Risk", f"{df['risk'].mean():.1f}%" if len(df) > 0 else "N/A")
    st.metric("Critical", len(df[df["level"] == "Critical"]))
    st.metric("Total Accidents (3mo)", df["accidents_3m"].sum())
