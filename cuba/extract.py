import requests
import json
import re
import csv

from pathlib import Path
from stem import Signal
from stem.control import Controller
from fake_useragent import UserAgent
from datetime import datetime
from bs4 import BeautifulSoup

proxies = {"http": "socks5h://127.0.0.1:9050", "https": "socks5h://127.0.0.1:9050"}

data = []
all_companies = []
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
    "Org_Revenue",
    "Leak_Links",
]
fieldnames.extend(additional_fieldnames)

# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller
    controller.authenticate()

    # Set the starting URL
    url = "http://cuba4ikm4jakjgmkezytyawtdgr2xymvy6nvzgw5cglswg3si76icnqd.onion"

    # Set the headers for the request
    headers = {"User-Agent": UserAgent().random}

    # Set the new IP address
    controller.signal(Signal.NEWNYM)

    # Send the request to the URL
    response = requests.get(f"{url}", headers=headers, proxies=proxies)
    soup = BeautifulSoup(response.content, "html.parser")

    # skip the first one because it's nothing
    free = soup.find(id="container-free")
    for company in free.find_all("div", "col-xs-12")[1:]:
        d = company.find("a")
        if d:
            all_companies.append(d["href"])

    for i in range(1, 7):
        # Send the request to the URL
        response = requests.get(
            f"{url}/ajax/page_free/{i}", headers=headers, proxies=proxies
        )

        soup = BeautifulSoup(response.content, "html.parser")

        for company in soup.find_all("div", "col-xs-12"):
            d = company.find("a")
            if d:
                all_companies.append(d["href"])

    for link in all_companies:
        # Send the request to the URL
        response = requests.get(url + link, headers=headers, proxies=proxies)

        soup = BeautifulSoup(response.content, "html.parser")
        page = soup.find("div", "page-content")

        # Parse the data
        org = page.find("span").text.strip()
        dl_link = page.find("div", "page-list-download").find("a")["href"]

        # Since there are 2 different formatting used by Cuba, we will format them individually
        # Format 1: contains "page-list-span" and "page-list-files"
        if page_span := page.find("div", "page-list-span"):
            description = ""
            for para in page_span.find_all("p"):
                para = para.text.replace("<br>", " ")
                description += para + ". "

            page_files = page.find("div", "page-list-files")
            if not page_files:
                print(f"Error! {org} is missing files")
            fdata = page_files.find_all("p")

            for d in fdata:
                search = d.text.split(":", 1)
                if len(search) < 2:
                    continue
                p1, p2 = search
                p2 = p2.strip()
                if "Date" in p1:
                    date = p2.strip()
                elif "website" in p1:
                    website = p2
                else:
                    # Remove last full stop character
                    tags = p2.replace(".", "").replace(", ", "|")

        # Format 2
        else:
            page_right = page.find("div", "page-list-right")
            if not page_right:
                print(f"{org} does not have right!")
                exit()
            all_paras = page_right.find_all("p")

            description = ""
            for i, para in enumerate(all_paras):
                if "\xa0" in para.text:
                    break
                description += para.text.strip() + ". "

            # Keep only the metadata
            for d in all_paras[i + 1 :]:
                search = d.text.split(":", 1)
                if len(search) < 2:
                    continue
                p1, p2 = search
                p2 = p2.strip()
                if "Date" in p1:
                    date = p2
                elif "website" in p1:
                    website = p2
                else:
                    # Remove last full stop character
                    tags = p2.replace(".", "").replace(", ", "|")

        # Check if within valid date range
        if "2022" not in date:
            continue

        dt_obj = datetime.strptime(date, "%d %B %Y")
        parsed_date = dt_obj.strftime("%d/%m/%Y")

        description.replace(",", " ")

        data.append(
            {
                "Organisation": org,
                "Org_URL": website,
                "Country": "NA",
                "Pub_Date": parsed_date,
                "Leak_Type": tags,
                "Description": description,
                "Ransom_URL": url + link,
                "Ransom_Group": "Cuba",
                "Leak_Links": dl_link,
                "Org_Revenue": "NA",
            }
        )


print(len(data))

Path("output").mkdir(parents=True, exist_ok=True)

with open("output/cuba.csv", newline="", mode="w", encoding="UTF8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

# f = open("output/sites.json", "w")
# f.write(json.dumps(data, indent=4))
