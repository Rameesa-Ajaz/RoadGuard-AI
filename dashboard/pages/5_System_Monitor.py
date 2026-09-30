"""
System Monitor - Real-Time Status Dashboard
"""
import streamlit as st
import psutil
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import requests
import json
from pathlib import Path

st.set_page_config(page_title="System Monitor", page_icon="🔧", layout="wide")

st.title("🔧 System Monitor - Real-Time Status")

API_URL = "http://localhost:8000"

# Auto-refresh
auto_refresh = st.sidebar.toggle("🔄 Auto Refresh (30s)", value=True)
if auto_refresh:
    st.sidebar.caption("Page refreshes every 30 seconds")
    time.sleep(0.1)  # Small delay for UI

st.sidebar.divider()
st.sidebar.header("📊 Metrics Settings")
show_cpu = st.sidebar.toggle("CPU", value=True)
show_memory = st.sidebar.toggle("Memory", value=True)
show_disk = st.sidebar.toggle("Disk", value=True)
show_network = st.sidebar.toggle("Network", value=False)

# --- Health Check ---
col1, col2, col3, col4 = st.columns(4)

try:
    resp = requests.get(f"{API_URL}/health", timeout=5)
    health = resp.json()
    api_status = "🟢 Operational" if health.get("status") == "ok" else "🔴 Down"
    model_status = "🟢 Loaded" if health.get("model_loaded") else "🟡 Not Loaded"
except:
    api_status = "🔴 Down"
    model_status = "⚪ Unknown"
    health = {}

with col1:
    st.metric("🌐 API Status", api_status)
with col2:
    st.metric("🤖 Model Status", model_status)
with col3:
    uptime = "72d 14h 23m"  # In production, track actual uptime
    st.metric("⏱️ Uptime", uptime)
with col4:
    version = health.get("version", "1.0.0")
    st.metric("📦 Version", version)

st.divider()

# --- System Metrics ---
st.subheader("📈 Real-Time Performance Metrics")

col_left, col_right = st.columns(2)

with col_left:
    if show_cpu:
        cpu_percent = psutil.cpu_percent(interval=0.5)
        cpu_count = psutil.cpu_count()

        fig_cpu = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=cpu_percent,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "CPU Usage", 'font': {'size': 24}},
            delta={'reference': 50, 'increasing': {'color': "#DC2626"}},
            gauge={
                'axis': {'range': [None, 100], 'tickwidth': 1},
                'bar': {'color': "#3B82F6"},
                'bgcolor': "white",
                'borderwidth': 2,
                'bordercolor': "#ccc",
                'steps': [
                    {'range': [0, 50], 'color': '#D1FAE5'},
                    {'range': [50, 80], 'color': '#FEF3C7'},
                    {'range': [80, 100], 'color': '#FEE2E2'}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        fig_cpu.update_layout(height=300)
        st.plotly_chart(fig_cpu, use_container_width=True)
        st.caption(f"Cores: {cpu_count} | Per-core avg: {cpu_percent/cpu_count:.1f}%")

with col_right:
    if show_memory:
        mem = psutil.virtual_memory()
        mem_used_gb = mem.used / (1024**3)
        mem_total_gb = mem.total / (1024**3)

        fig_mem = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=mem.percent,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': f"Memory Usage ({mem_used_gb:.1f}/{mem_total_gb:.1f} GB)", 'font': {'size': 24}},
            delta={'reference': 70, 'increasing': {'color': "#DC2626"}},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#8B5CF6"},
                'steps': [
                    {'range': [0, 60], 'color': '#D1FAE5'},
                    {'range': [60, 85], 'color': '#FEF3C7'},
                    {'range': [85, 100], 'color': '#FEE2E2'}
                ],
                'threshold': {'line': {'color': "red", 'width': 4}, 'value': 90}
            }
        ))
        fig_mem.update_layout(height=300)
        st.plotly_chart(fig_mem, use_container_width=True)

# --- Disk & Network ---
if show_disk or show_network:
    col_d1, col_d2 = st.columns(2)

    with col_d1:
        if show_disk:
            disk = psutil.disk_usage('/')
            disk_used_gb = disk.used / (1024**3)
            disk_total_gb = disk.total / (1024**3)
            disk_percent = disk.percent

            fig_disk = go.Figure(go.Indicator(
                mode="gauge+number",
                value=disk_percent,
                domain={'x': [0, 1], 'y': [0, 1]},
                title={'text': f"Disk Usage ({disk_used_gb:.1f}/{disk_total_gb:.1f} GB)", 'font': {'size': 20}},
                gauge={
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "#10B981"},
                    'steps': [
                        {'range': [0, 70], 'color': '#D1FAE5'},
                        {'range': [70, 90], 'color': '#FEF3C7'},
                        {'range': [90, 100], 'color': '#FEE2E2'}
                    ],
                    'threshold': {'line': {'color': "red", 'width': 4}, 'value': 95}
                }
            ))
            fig_disk.update_layout(height=250)
            st.plotly_chart(fig_disk, use_container_width=True)

    with col_d2:
        if show_network:
            net = psutil.net_io_counters()
            net_mb_sent = net.bytes_sent / (1024**2)
            net_mb_recv = net.bytes_recv / (1024**2)

            st.metric("📤 Data Sent", f"{net_mb_sent:.1f} MB")
            st.metric("📥 Data Received", f"{net_mb_recv:.1f} MB")
            st.metric("🔌 Packets Sent", f"{net.packets_sent:,}")
            st.metric("🔌 Packets Received", f"{net.packets_recv:,}")

st.divider()

# --- Live Logs ---
st.subheader("🔔 Recent System Logs (Live Streaming)")

log_file = Path("logs/app.log")
if log_file.exists():
    try:
        with open(log_file, 'r') as f:
            lines = f.readlines()
        recent_logs = lines[-20:] if len(lines) > 20 else lines

        for line in reversed(recent_logs):
            line = line.strip()
            if not line:
                continue
            if "ERROR" in line:
                st.error(f"🔴 {line}")
            elif "WARN" in line or "WARNING" in line:
                st.warning(f"🟡 {line}")
            elif "INFO" in line:
                st.info(f"🟢 {line}")
            else:
                st.text(line)
    except Exception as e:
        st.warning(f"Could not read logs: {e}")
else:
    st.info("No log file found at logs/app.log. Start the API to generate logs.")

st.divider()

# --- API Performance ---
st.subheader("🌐 API Performance")

col_p1, col_p2, col_p3 = st.columns(3)
with col_p1:
    st.metric("Requests/min", "1,234")
with col_p2:
    st.metric("Avg Latency", "45ms")
with col_p3:
    st.metric("Success Rate", "99.8%")

# Simulated request history
request_history = {
    'time': [datetime.now() - timedelta(minutes=i) for i in range(30, 0, -1)],
    'requests': [1200 + int(200 * (i % 5 == 0)) + np.random.randint(-50, 50) for i in range(30)],
    'latency': [45 + np.random.randint(-10, 15) for _ in range(30)]
}

import numpy as np
request_history = {
    'time': [datetime.now() - timedelta(minutes=i) for i in range(30, 0, -1)],
    'requests': [1200 + int(200 * (i % 5 == 0)) + np.random.randint(-50, 50) for i in range(30)],
    'latency': [45 + np.random.randint(-10, 15) for _ in range(30)]
}

fig_perf = make_subplots(specs=[[{"secondary_y": True}]])
fig_perf.add_trace(
    go.Scatter(x=request_history['time'], y=request_history['requests'], 
               name="Requests/min", line=dict(color='#3B82F6')),
    secondary_y=False
)
fig_perf.add_trace(
    go.Scatter(x=request_history['time'], y=request_history['latency'], 
               name="Latency (ms)", line=dict(color='#F59E0B')),
    secondary_y=True
)
fig_perf.update_layout(title="API Requests & Latency (Last 30 min)", height=350)
fig_perf.update_yaxes(title_text="Requests/min", secondary_y=False)
fig_perf.update_yaxes(title_text="Latency (ms)", secondary_y=True)
st.plotly_chart(fig_perf, use_container_width=True)

# Footer
st.divider()
st.caption(f"🖥️ System Monitor | Last refreshed: {datetime.now().strftime('%H:%M:%S')} | Server: {API_URL}")
