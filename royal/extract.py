import requests
import json
import csv

from pathlib import Path
from stem import Signal
from stem.control import Controller
from datetime import datetime
from fake_useragent import UserAgent
from bs4 import BeautifulSoup

proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

data = []

# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller
    controller.authenticate()

    # Set the starting URL
    base_url = "http://royal4ezp7xrbakkus3oofjw6gszrohpodmdnfbe5e4w3og5sm7vb3qd.onion/"
    url = base_url + "api/posts/list"

    # Set the headers for the request
    headers = {"User-Agent": UserAgent().random}

    # Set the new IP address
    controller.signal(Signal.NEWNYM)

    for page_num in range(1, 6):
        body = {"page": page_num}

        # Send the request to the URL
        response = requests.post(url, headers=headers, proxies=proxies, json=body)
        d = response.json()["data"]
        data.extend(d)

data = list(filter(lambda d: "2023" not in d["time"], data))

print(len(data))

# Parse the data into CSV format
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
additional_fieldnames = [
    "Leak_Size",
    "Org_Revenue",
    "Percentage_Leaked",
    "Leak_Links",
]
fieldnames.extend(additional_fieldnames)

# Clean the data a bit
cleaned = []
for d in data:
    dt_obj = datetime.strptime(d["time"], "%Y-%B-%d")
    parsed_date = dt_obj.strftime("%d/%m/%Y")

    parsed_text = BeautifulSoup(d["text"], "html.parser").get_text()
    parsed_text.replace(",", "")

    if len(d["size"]) == 0:
        size = 0
    else:
        size = d["size"]

    if len(d["revenue"]) == 0:
        revenue = 0
    else:
        revenue = d["revenue"]

    d2 = {
        "Organisation": d["title"],
        "Org_URL": d["url"],
        "Country": "NA",
        "Pub_Date": parsed_date,
        "Leak_Type": "NA",
        "Description": parsed_text,
        "Ransom_URL": base_url + d["id"],
        "Ransom_Group": "Royal",
        "Leak_Size": size,
        "Leak_Links": "||".join(d["links"]),
        "Org_Revenue": revenue,
        "Percentage_Leaked": d["percentage"],
    }

    cleaned.append(d2)

print(len(cleaned))

Path("output").mkdir(parents=True, exist_ok=True)

with open("output/royal.csv", newline="", mode="w", encoding="UTF8") as csvfile:
    fieldnames.extend(additional_fieldnames)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(cleaned)

# f = open("output/sites.json", "w")
# f.write(json.dumps(data, indent=4))
