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

import requests
from bs4 import BeautifulSoup


RE_CASE = re.compile(r"\bMál\s*(?:nr\.|:)\s*\(?\s*([A-Za-z]?\d+/\d{4})\s*\)?", re.IGNORECASE)





def fetch_and_parse(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; umbodsmadur-to-json/1.1)"}
    r = requests.get(url, headers=headers, timeout=30)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    main_heading = soup.find("h3")
    if not main_heading:
        raise RuntimeError("Could not find main heading on page")

    h1 = soup.find("h1")

    if not h1:
        raise RuntimeError("Could not find h1 on page")

    case_type = h1.get_text(strip=True)

    h3 = soup.find("h3")
    abstract = h3.get_text(strip=True) if h3 else None

    abstract = main_heading.get_text(strip=True)
    h4 = h3.find_next_sibling   ("h4") if h3 else None
    case_number = h4.get_text(strip=True) if h4 else None

    match = re.search(r"(\d+)/(\d+)", case_number)
    if match:
        case_id = int(match.group(1))  # 578
        year = int(match.group(2))  # 2025
    else:
        print("No numbers found")

    # Collect all <p> tags that follow the title
    paragraphs = []
    for elem in main_heading.find_all_next():
        # stop if we hit another major heading (optional)
        if elem.name == "h3":
            break
        if elem.name == "p":
            text = elem.get_text(" ", strip=True)
            if text:
                paragraphs.append({
                    "index": len(paragraphs),
                    "paragraphText": text
                })

    

    

    return {
        "title": f"{case_type} UA {case_number}/{year}",
        "originalUrl": url,
        "type": case_type,  #Determine Type: Detect if the item is an &quot;Opinion&quot; (Álit) or a &quot;Letter&quot; (Bréf).
        "abstract": abstract,
        "content": paragraphs,
    }

def fetch_and_parse2(url: str):
    headers = {"User-Agent": "Mozilla/5.0 (compatible; umbodsmadur-to-json/1.1)"}

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        print(f"Request failed: {e}")
        return None

    soup = BeautifulSoup(response.text, "lxml")

    h1 = soup.find("h1")
    h3 = soup.find("h3")

    if not h1 or not h3:
        raise RuntimeError(f"Required headings (h1 or h3) missing on page: {url}")

    case_type = h1.get_text(strip=True)
    abstract = h3.get_text(strip=True)
    h4 = h3.find_next_sibling   ("h4") if h3 else None
    case_number = h4.get_text(strip=True) if h4 else None

    match = re.search(r"(\d+)/(\d+)", case_number)
    if match:
        case_id = int(match.group(1))  # 578
        year = int(match.group(2))  # 2025
    else:
        print("No numbers found")

    # Collect all <p> tags that follow the title
    paragraphs = []
    current_node = (h4 if h4 else h3).next_sibling

    for elem in h3.find_all_next():
        # stop if we hit another major heading (optional)
        if elem.name == "h3":
            break
        if elem.name == "p":
            text = elem.get_text(" ", strip=True)
            if text:
                paragraphs.append({
                    "index": len(paragraphs),
                    "paragraphText": text
                })

    return {
        "title": f"{case_type} UA {case_id}/{year}",
        "case_id": case_id,
        "year": year,
        "originalUrl": url,
        "type": case_type,  #Determine Type: Detect if the item is an &quot;Opinion&quot; (Álit) or a &quot;Letter&quot; (Bréf).
        "abstract": abstract,
        "content": paragraphs,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("url", help="Umbodsmadur page URL")
    ap.add_argument("out", help="Output JSON file path, e.g. out.json")
    args = ap.parse_args()

    data = fetch_and_parse(args.url)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print("Wrote:", args.out)


if __name__ == "__main__":
    main()