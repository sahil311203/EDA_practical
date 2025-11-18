import streamlit as st
import pandas as pd
import json
import time

st.set_page_config(page_title="Smart Energy Dashboard", layout="wide")
st.title("💡 Smart Home Energy Dashboard")

col1, col2, col3 = st.columns(3)

with col1:
    temp_metric_placeholder = st.empty()
with col2:
    target_metric_placeholder = st.empty()
with col3:
    heater_metric_placeholder = st.empty()

time_status_placeholder = st.empty()

st.subheader("Temperature (Room vs. Target)")
chart_placeholder = st.empty()

st.subheader("Heater Activity (1 = ON, 0 = OFF)")
activity_placeholder = st.empty()

while True:
    try:
        data = []
        with open("processed_data.json", "r") as f:
            for line in f:
                try:
                    data.append(json.loads(line.strip()))
                except json.JSONDecodeError:
                    pass
        
        if not data:
            st.warning("Waiting for data...")
            time.sleep(3)
            continue

        df = pd.DataFrame(data[-50:]) # Show last 50 entries
        df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s')
        df = df.set_index('timestamp')

        # Get the most recent data point
        last_data = df.iloc[-1]
        
        # --- 1. Update Metrics ---
        temp_metric_placeholder.metric("Room Temperature", f"{last_data['temperature']} °C")
        target_metric_placeholder.metric("Target Temperature", f"{last_data['target_temp']} °C")
        heater_metric_placeholder.metric("Heater Status", last_data['heater_state'])

        # --- 2. Update Main Status ---
        if last_data['is_peak']:
            time_status_placeholder.error("⚡️ **TIME: PEAK HOURS** (Saving energy)")
        else:
            time_status_placeholder.success("✅ **TIME: OFF-PEAK** (Normal operation)")

        # --- 3. Update Line Chart ---
        # Plot both room temp and target temp
        chart_placeholder.line_chart(df[["temperature", "target_temp"]])

        # --- 4. Update Activity Chart ---
        # Convert "ON"/"OFF" to 1/0 for plotting
        df['heater_active'] = df['heater_state'].apply(lambda x: 1 if x == 'ON' else 0)
        activity_placeholder.bar_chart(df['heater_active'], color="#FF4B4a") # Red for heat

    except (FileNotFoundError, IndexError):
        time_status_placeholder.warning("Waiting for data...")
    except Exception as e:
        time_status_placeholder.error(f"An error occurred: {e}")

    time.sleep(3)