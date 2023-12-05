import requests
import json
import re
import csv
import time

from pathlib import Path
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from datetime import datetime
from bs4 import BeautifulSoup

proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

# Select the mode
collect_raw_data_mode = False

# -----------------------------------------------------
# Initial raw data collection
# -----------------------------------------------------
# Initialize the controller for the Tor network
if collect_raw_data_mode:
    all_companies = []
    with Controller.from_port(port=9051) as controller:
        # Set the controller
        controller.authenticate()

        # Set the starting URL
        url = "http://alphvmmm27o3abo3r2mlmjrpdmzle3rykajqc5xsj7j7ejksbpsa36ad.onion"

        # Set the headers for the request
        headers = {"User-Agent": UserAgent().random}

        # Set the new IP address
        controller.signal(Signal.NEWNYM)

        # Send the request to the URL
        # BlackCat need some sort of cookies to work!
        cookies = {"_dsi": "659419369881316054", "_dsk": "4967968257219353847"}

        raw_json_data = []

        for i in range(4, 29):
            response = requests.get(
                url + f"/api/blog/all/{9 * i}/9",
                headers=headers,
                proxies=proxies,
                cookies=cookies,
            )
            raw_json_data.extend(response.json()["items"])

    print(len(raw_json_data))

    f = open("output/sites.json", "w", encoding="UTF8")
    f.write(json.dumps(raw_json_data, indent=4))

    exit(0)

# ------------------------------------------------------
# END RAW DATA COLLECTIOn
# ------------------------------------------------------


# ------------------------------------------------------
# START RAW DATA PARSING
# ------------------------------------------------------
fieldnames = [
    "Organisation",
    "Org_URL",
    "Country",
    "Pub_Date",
    "Leak_Type",
    "Description",
    "Ransom_URL",
    "Ransom_Group",
]
additional_fieldnames = ["Org_Revenue", "Leak_Size", "Message", "Exact_Date"]
fieldnames.extend(additional_fieldnames)

with open("output/sites.json", "r", encoding="UTF8") as f:
    raw_data = json.load(f)

data = []

url = "http://alphvmmm27o3abo3r2mlmjrpdmzle3rykajqc5xsj7j7ejksbpsa36ad.onion/"
for d in raw_data:
    # Not all data have the additional metadata
    country, description, message, org_url = "NA", "NA", "NA", "NA"
    pub = d["publication"]
    if pub:
        if "url" in pub:
            org_url = pub["url"]
        if "country" in pub:
            country = pub["country"]
        if "description" in pub:
            description = pub["description"]
            description = description.replace("\n", " ")
        if "message" in pub:
            message = pub["message"]
            message = message.replace("\n", " ")

    # Parse date
    date = time.strftime("%d/%m/%Y", time.localtime(d["createdDt"]))
    exact_dt = time.strftime("%d/%m/%Y %H:%M:%S", time.localtime(d["createdDt"]))

    data.append(
        {
            "Organisation": d["title"],
            "Org_URL": org_url,
            "Country": country,
            "Pub_Date": date,
            "Leak_Type": "NA",
            "Description": description,
            "Ransom_URL": url + d["id"],
            "Ransom_Group": "BlackCat",
            "Leak_Size": "NA",
            "Org_Revenue": "NA",
            "Message": message,
            "Exact_Date": exact_dt,
        }
    )


Path("output").mkdir(parents=True, exist_ok=True)


with open("output/blackcat.csv", newline="", mode="w", encoding="utf8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
