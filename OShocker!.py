# OShocker!.py by SeMake

# Use program at your own risk, I am not responsible for any harm caused by shocking devices. 
# For safety on electric shocks check out "https://pishock.com/#/safety-section"

# Bare minumum libraries needed, make sure to have python3 and websockets, you can install websockets by "pip install websockets --user" 
import asyncio
import json
import websockets
import time

# Shocing related variables
shock_level = 0
shock_duration = 0
dyn_shock = False

# Keeps track of misses
last_misses = 0

# Time keeping
last_triggered = 0
cooldown = 0 # Seconds


# Determines the shock level and duration, then starts the websocket connection at miss_tracking()
def setup():
    global shock_level, shock_duration, cooldown, dyn_shock
    print("Entering Setup Mode")
    print()
    while True:
        shock_level = int(input("Type in your desired shock level (0-100%, 0 for vibration only) and press Enter: ")) # Shock intensity 0-100, 0 is just vibration
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

    dyn_shock = input("Do you want to enable dynamic shock? Increases shock level with each miss by 5% (y/n): ").lower()
    if dyn_shock == "y":
        dyn_shock = True
    else:
        dyn_shock = False

    print(f"Shock level: {shock_level}%, Duration: {shock_duration} seconds, Dynamic Shock: {dyn_shock}")
    print()
    input("Press Enter to confirm settings and that tosu is running...")
    print("Program initialized!")
    asyncio.run(miss_tracking())

async def miss_tracking():
    global shock_level, shock_duration, dyn_shock, last_misses, last_triggered, cooldown
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
                            print(f"Shock! Total misses this song: {last_misses + 1}") # Miss count is one higher than the last check, because you just got a new miss
                            last_triggered = now # Starts cooldown

                            if dyn_shock: # If dynamic shock is enabled, increase shock level by 5% for every miss, up to a maximum of 100%
                                if modified_shock_level + 5 <= 100:
                                    modified_shock_level += 5
                                    print(f"Shock level increased to {modified_shock_level}% due to dynamic shock!")
                                    print()

                        last_misses = misses # Updates last_misses to the current miss count for the next check

                    except KeyError: 
                        pass
        
        except Exception: # Allows for retry if tosu is unreachable
            print("Cannot reach tosu! :c")
            input("Press Enter to retry or Ctrl+C to exit...")

setup() # Starts the program, asking for shock settings and then starting the websocket connection

