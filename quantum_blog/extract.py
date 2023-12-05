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
additional_fieldnames = ["Views", "Leak_Size", "Org_Revenue", "Percentage_Leaked"]
data = []
websites = []

# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller
    controller.authenticate()

    # Set the starting URL
    url = "http://quantum445bh3gzuyilxdzs5xdepf3b7lkcupswvkryf3n7hgzpxebid.onion"

    # Set the headers for the request
    headers = {"User-Agent": UserAgent().random}

    # Set the new IP address
    controller.signal(Signal.NEWNYM)

    # Send the request to the URL
    response = requests.get(url, headers=headers, proxies=proxies)

    soup = BeautifulSoup(response.content, "html.parser")

    # Round 1: Get all the relevant groups
    for post in soup.find_all("section", "blog-post"):
        date = post.find("p", "blog-post-date").text

        if "2022" not in date:
            continue

        link = post.find("a")["href"]

        websites.append(link)

    print(len(websites))

    # Round 2: Get more details about each group
    for website in websites:
        try:
            # Send the request to the URL
            response = requests.get(url + website, headers=headers, proxies=proxies)
            site = BeautifulSoup(response.content, "html.parser")

            size = site.find("span", "label-light").text.strip()
            views = site.find("span", "btn").text.split("\n")[0].strip()
            date = site.find("p", "blog-post-date").text.strip()
            dt_obj = datetime.strptime(date, "%Y-%m-%d")
            date = dt_obj.strftime("%d/%m/%Y")

            all_details = site.find_all("dd", "col-sm-9")
            org_name, _, total_revenue, _, vol_data_leaked = list(
                map(lambda a: a.get_text().strip(), all_details)
            )

            org_url = all_details[1].find("a")["href"].strip()

            others = site.find_all("div", "col-md-4")[1]
            description = others.find("p", class_=None)
            if description:
                description = description.text
                description = re.sub(r"[\n\t]*", "", description).strip()
            else:
                description = "NA"

            data.append(
                {
                    "Organisation": org_name,
                    "Org_URL": org_url,
                    "Country": "NA",
                    "Pub_Date": date,
                    "Leak_Type": "NA",
                    "Description": description,
                    "Ransom_URL": url + website,
                    "Ransom_Group": "Quantum Blog",
                    "Views": views,
                    "Leak_Size": size,
                    "Org_Revenue": total_revenue,
                    "Percentage_Leaked": vol_data_leaked,
                }
            )
        except Exception as e:
            print(e)
            print(website)
            continue


print(len(data))

Path("output").mkdir(parents=True, exist_ok=True)

with open("output/quantum.csv", newline="", mode="w", encoding="UTF8") as csvfile:
    fieldnames.extend(additional_fieldnames)
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)
