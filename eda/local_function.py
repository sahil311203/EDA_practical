# Updated: local_function.py
import json
import time
import os
import datetime

# File definitions
IOT_FILE = "iot_messages.json"
PROCESSED_FILE = "processed_data.json"
ACTUATOR_FILE = "actuator_state.json"
SETTINGS_FILE = "system_settings.json"

def get_system_settings():
    """Reads user-defined settings."""
    default_settings = {
        "target_temp": 20.0,
        "peak_start_hour": 16, # 4 PM
        "peak_end_hour": 20   # 8 PM
    }
    if not os.path.exists(SETTINGS_FILE):
        return default_settings
    try:
        with open(SETTINGS_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default_settings

def get_actuator_state():
    """Reads the current state of the heater."""
    if not os.path.exists(ACTUATOR_FILE):
        return {"heater": "OFF"}
    try:
        with open(ACTUATOR_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"heater": "OFF"}

def set_actuator_state(new_state):
    """Writes the new state to the heater file."""
    with open(ACTUATOR_FILE, "w") as f:
        json.dump(new_state, f)

def is_peak_time(settings):
    """Checks if the current time is within peak hours."""
    current_hour = datetime.datetime.now().hour
    return settings["peak_start_hour"] <= current_hour < settings["peak_end_hour"]

def process_message(data):
    room_temp = data.get("temperature")
    if room_temp is None:
        return

    # --- Smart Control Logic ---
    settings = get_system_settings()
    target = settings["target_temp"]
    is_peak = is_peak_time(settings)

    current_state = get_actuator_state().get("heater", "OFF")
    new_state = current_state # Assume no change by default

    if room_temp < target and current_state == "OFF":
        # Room is cold, should we turn on the heater?
        if not is_peak:
            print(f"✅ Temp below target ({room_temp}°C) & OFF-PEAK. Turning Heater ON.")
            new_state = "ON"
        else:
            print(f"⚡️ Temp below target ({room_temp}°C) but PEAK HOURS. Staying OFF to save.")
            
    elif room_temp > (target + 1) and current_state == "ON":
        # Room is warm enough, turn off heater
        print(f"🌡️ Target reached ({room_temp}°C). Turning Heater OFF.")
        new_state = "OFF"
    # --- End Logic ---

    if new_state != current_state:
        set_actuator_state({"heater": new_state})

    # Save processed data for the dashboard
    data["heater_state"] = new_state
    data["target_temp"] = target
    data["is_peak"] = is_peak
    with open(PROCESSED_FILE, "a") as f:
        f.write(json.dumps(data) + "\n")

if __name__ == "__main__":
    print("🤖 Smart Home Energy Hub started. Monitoring data...")
    if os.path.exists(IOT_FILE):
        os.remove(IOT_FILE)

    while True:
        try:
            with open(IOT_FILE, "r+") as f:
                lines = f.readlines()
                f.truncate(0) # Clear file after reading
            
            for line in lines:
                try:
                    data = json.loads(line.strip())
                    process_message(data)
                except json.JSONDecodeError:
                    print(f"Skipping malformed data: {line}")
        except FileNotFoundError:
            pass
        
        time.sleep(3)