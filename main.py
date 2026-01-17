#!/usr/bin/env python3
# umbodsmadur_to_json.py
#
# pip install requests beautifulsoup4 lxml
#
# Usage:
#   py -3.14 umbodsmadur_to_json.py "https://www.umbodsmadur.is/alit-og-bref/mal/nr/11106/skoda/mal/" out.json

import argparse
import json
import re

from urllib.parse import urljoin

import requests
import time

from html2json import fetch_and_parse2

from bs4 import BeautifulSoup




CASES_URL = "https://www.umbodsmadur.is/api/cases/SearchCases"

params = {
    "searchWordID": 0,
    "institutionID": 0,
    "count": 10000,   # larger = fewer requests
    "skip": 0
}

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0"
})






response = session.get(CASES_URL, params=params, timeout=30)
response.raise_for_status()

data = response.json()

list = []

for item in data.get("alitItems", []):
    url = f"https://www.umbodsmadur.is/alit-og-bref/mal/nr/{item["lykill"]}/skoda/mal/"
    try:
        list.append(fetch_and_parse2(url))
    except RuntimeError as e:
        print("Caught a runtime error:", e)
    if len(list) % 10 == 0:
        print(f"Fetched {len(list)} cases so far...")

json_string = json.dumps(list, ensure_ascii=False, indent=2)

with open("output.json", "w", encoding="utf-8") as f:
    f.write(json_string)



print("Output written to file output.json")    

print("Done.")


