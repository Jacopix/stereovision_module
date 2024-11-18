import webbrowser
import json
import time


urls = []

# Get all compatible cameras
with open('compatible_cameras.json', 'r') as file:
    data = json.load(file)

# Add to search_terms
for camera in data["lowlight_cameras"]:
    urls.append(camera["link"])
    

# Search on google
for url in urls:
    webbrowser.open_new_tab(url)
    time.sleep(0.5) # Sleep otherwise google detects it
