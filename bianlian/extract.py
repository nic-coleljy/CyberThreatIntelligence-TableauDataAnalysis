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
    "Leak_Size",
    "Tags",
    "Leak_Links",
]
fieldnames.extend(additional_fieldnames)

# Initialize the controller for the Tor network
with Controller.from_port(port=9051) as controller:
    # Set the controller
    controller.authenticate()

    # Set the starting URL
    url = "http://bianlianlbc5an4kgnay3opdemgcryg2kpfcbgczopmm3dnbz3uaunad.onion"

    # Set the headers for the request
    headers = {"User-Agent": UserAgent().random}

    # Set the new IP address
    controller.signal(Signal.NEWNYM)

    # Send the request to the URL
    response = requests.get(url + "/companies", headers=headers, proxies=proxies)

    soup = BeautifulSoup(response.content, "html.parser")

    for company in soup.find_all("li", "post"):
        date = company.find("span", "meta").text.strip()

        if "2022" not in date:
            continue

        dt_obj = datetime.strptime(date, "%b %d, %Y")
        parsed_date = dt_obj.strftime("%d/%m/%Y")

        d = company.find("a")

        all_companies.append({"name": d.text, "link": d["href"], "date": date})

    print(len(all_companies))
    # print(all_companies)

    for i, group in enumerate(all_companies):
        print(f"Scrape {group['name']}")
        # Send the request to the URL
        response = requests.get(url + group["link"], headers=headers, proxies=proxies)

        soup = BeautifulSoup(response.content, "html.parser")
        article = soup.find("article")

        # Parse the data
        org = article.find("h1", "title").text.strip()

        # Hidden company names will not have links
        if "**" in org:
            description = article.select_one("p:nth-of-type(1)").text
            org_link = "Hidden"
            dl_link = "Hidden"
        else:
            description = article.select_one("p:nth-of-type(2)").text
            org_link = article.find("a")["href"]
            links = article.find_all("p")[-1].find("a")
            if links:
                dl_link = links["href"].strip()
            else:
                dl_link = "None"

        description = re.sub(r"[\n\t]*", "", description).strip()

        size = "NA"
        revenue = "NA"
        raw_text = article.find_all("p")

        for para in raw_text:
            if "Volume" in para.text:
                size = para.text.split(":")[1].strip()
            if "Revenue" in para.text:
                # Convert the American style of currency to SG style
                t = para.text
                revenue = t[t.index("$") :]
                revenue = revenue.strip().replace(",", ".")

        # Look for leaked data characteristics
        leaked_types = []
        u_list = article.find_all("ul", class_=None)
        if u_list:
            for u in u_list:
                for li in u.find_all("li"):
                    leaked_types.append(li.text.strip())

        # Look for tags
        tags = []
        all_tags = article.find("ul", "tags")
        if all_tags:
            for li in all_tags.find_all("li"):
                tags.append(li.text.strip())

        data.append(
            {
                "Organisation": org,
                "Org_URL": org_link,
                "Country": "NA",
                "Pub_Date": group["date"],
                "Leak_Type": "|".join(leaked_types),
                "Description": description,
                "Ransom_URL": url + group["link"],
                "Ransom_Group": "Bianlian",
                "Leak_Links": dl_link,
                "Leak_Size": size,
                "Org_Revenue": revenue,
                "Tags": "|".join(tags),
            }
        )


print(len(data))

Path("output").mkdir(parents=True, exist_ok=True)


with open("output/bianlian.csv", newline="", mode="w", encoding="UTF8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(data)

# f = open("output/sites.json", "w")
# f.write(json.dumps(data, indent=4))
