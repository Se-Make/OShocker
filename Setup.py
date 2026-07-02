import time
import requests
import subprocess
import sys

subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt", "--target", "."])

SHOCKER_UUID = ""
API_TOKEN = ""

def send_control(SHOCKER_UUID: str, API_TOKEN: str, control_type: str, intensity: int, duration_ms: int):
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


print("This is a setup for OShocker! by SeMake")
time.sleep(2)

print("For setup you will need an OpenShock account and an API token. Make sure you have your shocker and hub turned on.")
time.sleep(2)

print("You can generate an API token in your OpenShock account settings at https://openshock.app/settings/api-tokens")
time.sleep(2)

print("Never show your API token to anyone else, as it can be used to control your shockers!")
time.sleep(2)
print()

input("Press Enter to continue after you have your API token copied...")
API_TOKEN = input("Enter your OpenShock API token: ")
time.sleep(2)
print()

print("Great! Now for the final step, you need to get your shocker's UUID at https://openshock.app/shockers/own.")
time.sleep(2)

print("Click on the 3 dots next to your shocker, then click 'Copy ID' to copy it to your clipboard.")
time.sleep(2)
print()

input("Press Enter to continue after you have your Shocker UUID copied...")
SHOCKER_UUID = input("Enter your shocker's UUID: ")
time.sleep(2)

print("Perfect, your configuration is now saved, if you made a mistake, you can run this program again!")
print()

with open("config.txt", "w") as config_file:
    config_file.write(f"{API_TOKEN}\n")
    config_file.write(f"{SHOCKER_UUID}\n")
time.sleep(2)
print("Sending a test vibration to make sure connection works...")
time.sleep(2)

try:
    send_control(SHOCKER_UUID, API_TOKEN, "vibrate", 50, 1000)
    print("Test vibration sent successfully! Your setup is complete!")
except Exception as e:
    print(f"An error occurred while sending the test vibration: {e}")


print("Closing setup in 5...")
time.sleep(1)
print("4...")
time.sleep(1)
print("3...")
time.sleep(1)
print("2...")
time.sleep(1)
print("1...")
time.sleep(1)

