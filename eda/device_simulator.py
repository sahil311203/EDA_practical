# Updated: device_simulator.py
import time, json, random, os

ACTUATOR_FILE = "actuator_state.json"

def get_actuator_state():
    """Reads the current state of the heater actuator."""
    if not os.path.exists(ACTUATOR_FILE):
        return {"heater": "OFF"}
    try:
        with open(ACTUATOR_FILE, "r") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {"heater": "OFF"}

def send_data(current_temp):
    """Simulates a thermostat sending data, with responsive temperature."""
    while True:
        state = get_actuator_state()
        heater_status = state.get("heater", "OFF")

        # --- Smart Simulation Logic ---
        # Simulate temperature changing based on heater status
        if heater_status == "ON":
            # Heater is ON, temperature increases
            temp_change = random.uniform(0.4, 0.8)
            current_temp = min(25, current_temp + temp_change) # Cap at 25°C
        else:
            # Heater is OFF, temperature slowly decreases (losing heat)
            temp_change = random.uniform(-0.3, -0.1)
            current_temp = max(15, current_temp + temp_change) # Floor at 15°C
        
        current_temp = round(current_temp, 2)
        # --- End Smart Logic ---

        data = {
            "device_id": "thermostat01",
            "temperature": current_temp,
            "timestamp": time.time()
        }
        
        # Save to file to simulate message queue
        with open("iot_messages.json", "a") as f:
            f.write(json.dumps(data) + "\n")
        
        print(f"Sent: Room Temp={current_temp}°C, Heater: {heater_status}")
        time.sleep(3)

if __name__ == "__main__":
    # Start with a cool room
    initial_temp = 18.0
    send_data(initial_temp)