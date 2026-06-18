# OShocker!.py by SeMake

# Use program at your own risk, I am not responsible for any harm caused by shocking devices. 
# For safety on shock collars and the like, check out "https://wiki.openshock.org/home/safety-rules"

# Bare minumum libraries needed, make sure to have python3, websockets and requests installed to run this program.
import asyncio
import json
import websockets
import requests
import time

# Configuration variables
SHOCKER_UUID = ""
API_TOKEN = ""

# Shocking related variables
shock_level = 0
shock_cap = 100
shock_duration = 0
dyn_shock = False
control_type = ""

# Keeps track of misses
last_misses = 0

# Time keeping
last_triggered = 0
cooldown = 0 # Seconds

try:
    f = open("config.txt")
except FileNotFoundError:
    print("No config file found, run setup.py to create one...")
else:
    with f:
        lines = f.read().splitlines()
        API_TOKEN = lines[0]
        SHOCKER_UUID = lines[1]


# Determines the shock level and duration, then starts the websocket connection at miss_tracking()
def setup():
    global shock_level, shock_duration, cooldown, dyn_shock, control_type, shock_cap
    print("Entering Setup Mode")
    print()
    while True:
        shock_level = int(input("Type in your desired shock level (0-100%, 0 for vibration only) and press Enter: ")) # Shock intensity 0-100, 0 is just vibration
        if shock_level == 0:
            control_type = "vibrate"
        else:
            control_type = "shock"
        if shock_level < 0 or shock_level > 100:
            print("Invalid shock level! Please enter a value between 0 and 100.")
            print()
        else: break   

    while True:
        shock_duration = int(input("Now for the duration of the shock (1-10 seconds): ")) # How long the shock should last in seconds, 1-10 
        if shock_duration < 1 or shock_duration > 10:
            print("Invalid duration! Please enter a value between 1 and 10.")
            print()
        else: break  

    while True:
        cooldown = int(input("Enter cooldown time between shocks (0-10 seconds): ")) # How long the program should wait after a shock before it can shock again, 0-10 seconds
        if cooldown < 0 or cooldown > 10:
            print("Invalid cooldown! Please enter a value between 0 and 10.")
            print()
        else: break  

    dyn_shock = input("Do you want to enable dynamic shock? Increases shock level with each miss by 5% (y/n): ").lower() # Dynamic shock increases shock level by 5% for every miss, up to a maximum of shock_cap
    if dyn_shock == "y":
        dyn_shock = True
        while True:
            shock_cap = int(input("Enter the maximum shock level for dynamic shock (5-100%): ")) # Maximum shock level for dynamic shock, 5-100%
            if shock_cap < 5 or shock_cap > 100:
                print("Invalid shock cap! Please enter a value between 5 and 100.")
                print()
            else: break
    else:
        dyn_shock = False

    print(f"Shock level: {shock_level}%, Duration: {shock_duration} seconds, Dynamic Shock: {dyn_shock}, Shock Cap: {shock_cap}%")
    print()
    input("Press Enter to confirm settings and that tosu is running...")
    print("Program initialized!")
    asyncio.run(miss_tracking())


def send_control(SHOCKER_UUID, API_TOKEN, control_type, intensity, duration_ms): # Function to send control signals to the shocker using the OpenShock API
    url = "https://api.openshock.app/1/shockers/control"
    headers = {
        "OpenShockToken": API_TOKEN,
        "Content-Type": "application/json",
    }
    payload = [
        {
            "id": SHOCKER_UUID,
            "type": control_type,
            "intensity": intensity,
            "duration": duration_ms,
            "exclusive": True,
        }
    ]

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    return response

async def miss_tracking():
    global shock_level, shock_duration, dyn_shock, last_misses, last_triggered, cooldown, control_type, shock_cap, SHOCKER_UUID, API_TOKEN
    modified_shock_level = shock_level # Making sure that the base shock level is not changed by dynamic shock, so that it can be reset at the start of each map
    map_reset = False # Variable to track if the map has been reset, to prevent multiple resets during the first 100ms of the map

    while True:
        try:
            async with websockets.connect("ws://127.0.0.1:24050/websocket/v2") as ws: # Connects to tosu websocket, make sure tosu is running.
                print("Ready to shock :3c")

                while True:
                    msg = await ws.recv() # Raw payload from tosu websocket
                    data = json.loads(msg) # Makes a dictionary with all the data from tosu
                    now = time.time() # Looks at time for cooldowns

                    try:
                        misses = data["play"]["hits"]["0"] # Reads misses from the json data
                        map_timer = data["beatmap"]["time"]["live"] # Reads milliseconds since the map started


                        if map_timer < 100 and not map_reset: # Resets shock levels and score if reset or map change detected
                            last_triggered = 0
                            modified_shock_level = shock_level
                            last_misses = 0
                            map_reset = True
                            print("Shock and score reset due to new map or retry.")

                        if map_timer >= 100:
                            map_reset = False  # Ready to detect the next reset

                        if (misses > last_misses) and ((now - last_triggered) >= cooldown): # If you have more misses than the last check and the cooldown has passed, trigger shock
                            print(f"Miss! Total misses this song: {last_misses + 1}") # Miss count is one higher than the last check, because you just got a new miss
                            last_triggered = now # Starts cooldown

                            if dyn_shock: # If dynamic shock is enabled, increase shock level by 5% for every miss, up to a maximum of shock_cap
                                if modified_shock_level + 5 <= shock_cap:
                                    modified_shock_level += 5
                                    print(f"Shock level increased to {modified_shock_level}% due to dynamic shock!")
                                    print()
                            send_control(SHOCKER_UUID, API_TOKEN, control_type, modified_shock_level, shock_duration * 1000) # Sends the shock or vibration command to the shocker

                        last_misses = misses # Updates last_misses to the current miss count for the next check

                    except KeyError: 
                        pass
        
        except Exception: # Allows for retry if tosu is unreachable
            print("Cannot reach tosu! :c")
            input("Press Enter to retry or Ctrl+C to exit...")

setup() # Starts the program, asking for shock settings and then starting the websocket connection

