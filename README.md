# CS445 Cyber Threat Intelligence Group Project

This repo contains the scripts and collected data from the various ransomware groups in the year 2022

## Getting Started

Each ransomware group has their data collection scripts and raw output data included in a single folder.
They contain:

- script(s) (usually in Python) to collect the necessary data
- output folder which contains the scraped data

### Others

- The `Python - Transpose rows and finalising dataset` folder contains scripts which perform data post-processing and cleaning such that they would be ready to be imported into Tableau for data visualisation.
- The Tableau files (.twbx) that was used are also included
  - `445 Project.twbx` - main file which contains the different dashboards and visualisations
  - `445 Project - Leaks.twbx` - additional file which contains the various leak data types and size by the different groups
- The main report in both PDF and DOCX versions
- Other excel sheets used to collate data (Data Compilation.xlsx)

## Requirements

The system should have:

- TOR bridge installed
- SOCKS5h proxy installed preferrably for scraping
- Python3+
- Python3-venv
- Pip3

### Installation

Perform the installation of required modules.

```bash
# Required packages
sudo apt install tor python3-pip python3-venv

# Edit the tor service
# First: cd /etc/tor
# Then: sudo chmod o+w torrc
sudo echo "ControlPort 9051" >> /etc/tor/torrc
sudo echo "CookieAuthentication 1" >> /etc/tor/torrc
# When done: sudo chmod o-w torrc

# Start the service
sudo service tor start

# Create virtual env
python3 -m venv ../cs445
source ../cs445/bin/activate

# Install modules individually (recommended)
pip3 install beautifulsoup4
pip3 install requests
pip3 install requests[socks]
pip3 install requests[security]
pip3 install cryptography
pip3 install stem
pip3 install fake-useragent

# Install using requirements.txt
pip3 install -r requirements.txt
```
