import time

import pandas as pd
import requests
import streamlit as st

BASE_URL = "http://localhost:8000"
API_KEY = "dev-secret-key"


@st.cache_data(ttl=2)
def fetch_metrics() -> dict:
    try:
        return requests.get(f"{BASE_URL}/metrics", timeout=3).json()
    except Exception:
        return {}


@st.cache_data(ttl=5)
def fetch_servers() -> list[dict]:
    try:
        return requests.get(f"{BASE_URL}/servers", timeout=3).json()
    except Exception:
        return []


def status_color(val: str) -> str:
    colors = {"UP": "background-color: #d4edda", "DEGRADED": "background-color: #fff3cd", "DOWN": "background-color: #f8d7da"}
    return colors.get(val, "")


st.set_page_config(page_title="DevOps Monitor", layout="wide")
st.title("DevOps Monitoring Dashboard")

tab_metrics, tab_servers = st.tabs(["Metrics", "Servers"])

# --- Tab 1: live metrics ---
with tab_metrics:
    placeholder = st.empty()

    if "history" not in st.session_state:
        st.session_state.history = []

    data = fetch_metrics()
    if data:
        ts = time.time()
        st.session_state.history.append(
            {"time": ts, "cpu": data.get("cpu_percent", 0), "memory": data.get("memory_percent", 0)}
        )
        # keep only last 60 points
        st.session_state.history = st.session_state.history[-60:]

        with placeholder.container():
            col1, col2, col3 = st.columns(3)
            col1.metric("CPU %", f"{data.get('cpu_percent', 0):.1f}%")
            col2.metric("Memory %", f"{data.get('memory_percent', 0):.1f}%")
            col3.metric("Disk %", f"{data.get('disk_percent', 0):.1f}%")

            if len(st.session_state.history) > 1:
                df = pd.DataFrame(st.session_state.history).set_index("time")
                st.line_chart(df[["cpu", "memory"]])
    else:
        st.error("Cannot reach the API backend.")

    time.sleep(2)
    st.rerun()

# --- Tab 2: servers ---
with tab_servers:
    servers = fetch_servers()

    if servers:
        df = pd.DataFrame(servers)
        styled = df.style.applymap(status_color, subset=["status"])
        st.dataframe(styled, use_container_width=True)
    else:
        st.info("No servers registered yet.")

    st.subheader("Register a new server")
    with st.form("add_server"):
        name = st.text_input("Name")
        host = st.text_input("Host", value="localhost")
        port = st.number_input("Port", min_value=1, max_value=65535, value=8000)
        submitted = st.form_submit_button("Add Server")
        if submitted:
            resp = requests.post(
                f"{BASE_URL}/servers",
                json={"name": name, "host": host, "port": int(port)},
                headers={"X-API-Key": API_KEY},
                timeout=5,
            )
            if resp.status_code == 201:
                st.success(f"Server '{name}' added!")
                fetch_servers.clear()
            else:
                st.error(f"Error {resp.status_code}: {resp.text}")

    st.subheader("Trigger health check")
    if servers:
        options = {s["name"]: s["id"] for s in servers}
        selected_name = st.selectbox("Select server", list(options.keys()))
        if st.button("Check now"):
            sid = options[selected_name]
            resp = requests.post(f"{BASE_URL}/servers/{sid}/check", timeout=5)
            if resp.status_code == 200:
                st.success("Health check triggered — refresh in a moment.")
                fetch_servers.clear()
            else:
                st.error(f"Error: {resp.text}")
