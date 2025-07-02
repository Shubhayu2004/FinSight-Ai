import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import quote, urljoin
from bs4.element import Tag

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def google_search(query, num_results=5):

    search_url = f"https://duckduckgo.com/html/?q={quote(query)}"
    resp = requests.get(search_url, headers=HEADERS, timeout=10)
    soup = BeautifulSoup(resp.text, "html.parser")
    links = []
    for a in soup.select("a.result__a"):
        if isinstance(a, Tag):
            href = a.get("href", "")
            if isinstance(href, str) and href.startswith("http"):
                links.append(href)
            if len(links) >= num_results:
                break
    return links

def find_annual_report_link(website_url):

    try:
        resp = requests.get(website_url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")
        # Look for links with 'annual report' and PDF
        links = soup.find_all("a", href=True)
        candidates = []
        for link in links:
            if not isinstance(link, Tag):
                continue
            text = link.get_text(" ").lower()
            href = link.get("href", None)
            if isinstance(href, str):
                href_l = href.lower()
                if ("annual report" in text or "annual report" in href_l) and href_l.endswith(".pdf"):
                    candidates.append(href_l)
        # Prefer links with years (latest first)
        candidates = sorted(candidates, key=lambda x: re.findall(r"20\\d{2}", x), reverse=True)
        if candidates:
            # Make absolute URL if needed
            pdf_url = candidates[0]
            if not pdf_url.startswith("http"):
                pdf_url = urljoin(website_url, pdf_url)
            return pdf_url
        # If not found, look for 'investor', 'financial', or 'annual' pages
        for link in links:
            if not isinstance(link, Tag):
                continue
            href = link.get("href", None)
            if isinstance(href, str):
                href_l = href.lower()
                if any(word in href_l for word in ["investor", "financial", "annual"]):
                    if not href_l.startswith("http"):
                        href_full = urljoin(website_url, href_l)
                    else:
                        href_full = href_l
                    # Recursively search this page
                    try:
                        sub_resp = requests.get(href_full, headers=HEADERS, timeout=10)
                        sub_soup = BeautifulSoup(sub_resp.text, "html.parser")
                        sub_links = sub_soup.find_all("a", href=True)
                        for sub_link in sub_links:
                            if not isinstance(sub_link, Tag):
                                continue
                            sub_text = sub_link.get_text(" ").lower()
                            sub_href = sub_link.get("href", None)
                            if isinstance(sub_href, str):
                                sub_href_l = sub_href.lower()
                                if ("annual report" in sub_text or "annual report" in sub_href_l) and sub_href_l.endswith(".pdf"):
                                    pdf_url = sub_href_l
                                    if not pdf_url.startswith("http"):
                                        pdf_url = urljoin(href_full, pdf_url)
                                    return pdf_url
                    except Exception:
                        continue
        return None
    except Exception as e:
        print(f"Error scraping {website_url}: {e}")
        return None

def fetch_latest_annual_report(company_name):
    print(f"Searching for official website of {company_name}...")
    search_results = google_search(f"{company_name} official website")
    if not search_results:
        return None
    for url in search_results:
        print(f"Trying {url}...")
        pdf_link = find_annual_report_link(url)
        if pdf_link:
            print(f"Found annual report: {pdf_link}")
            return pdf_link
    print("No annual report found.")
    return None

# Example usage:
# link = fetch_latest_annual_report("Tata Consultancy Services")
# print(link)
