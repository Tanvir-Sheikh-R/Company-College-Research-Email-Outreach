import httpx
from bs4 import BeautifulSoup
import re
from typing import List, Dict, Optional
import time
import urllib.parse

BLOCKED_DOMAINS = {
    "example.com", "domain.com", "yourdomain.com",
    "gmail.com", "yahoo.com", "hotmail.com", "outlook.com",
    "aol.com", "icloud.com", "protonmail.com", "mail.com",
}

NON_COMPANY_DOMAINS = {
    "wikipedia.org", "youtube.com", "facebook.com", "twitter.com",
    "linkedin.com", "instagram.com", "reddit.com", "pinterest.com",
    "yelp.com", "yellowpages.com", "glassdoor.com", "indeed.com",
    "trustpilot.com", "g2.com", "capterra.com", "upwork.com",
    "fiverr.com", "craigslist.org", "ebay.com", "amazon.com",
}

class ExtractAgent:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def is_likely_company_site(self, url: str) -> bool:
        domain = urllib.parse.urlparse(url).netloc.lower()
        for blocked in NON_COMPANY_DOMAINS:
            if blocked in domain:
                return False
        return True

    def fetch_page(self, url: str) -> Optional[str]:
        try:
            resp = httpx.get(url, headers=self.headers, timeout=15, follow_redirects=True)
            if resp.status_code == 200:
                return resp.text
        except:
            return None

    def get_page_text(self, url: str) -> str:
        html = self.fetch_page(url)
        if not html:
            return ""
        soup = BeautifulSoup(html, "lxml")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        text = soup.get_text(separator=" ", strip=True)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:3000]

    def extract_emails(self, html: str) -> List[str]:
        emails = set()
        pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        for match in re.finditer(pattern, html):
            email = match.group().lower()
            domain = email.split("@")[1]
            if domain not in BLOCKED_DOMAINS:
                emails.add(email)
        return list(emails)

    def extract_company_info(self, url: str) -> Dict:
        info = {"url": url, "name": "", "phone": "", "emails": [], "socials": [],
                "description": "", "page_text": ""}
        if not self.is_likely_company_site(url):
            return info

        html = self.fetch_page(url)
        if not html:
            return info

        soup = BeautifulSoup(html, "lxml")
        title_tag = soup.find("title")
        info["name"] = title_tag.get_text(strip=True) if title_tag else ""

        meta_desc = soup.find("meta", attrs={"name": "description"})
        if meta_desc and meta_desc.get("content"):
            info["description"] = meta_desc["content"].strip()[:300]

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        info["page_text"] = re.sub(r'\s+', ' ', soup.get_text(separator=" ", strip=True)).strip()[:3000]

        emails = self.extract_emails(html)
        info["emails"] = emails

        phone_pattern = r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]'
        phones = re.findall(phone_pattern, html)
        info["phone"] = phones[0].strip() if phones else ""

        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "linkedin.com" in href:
                info["socials"].append(href)
            elif "facebook.com" in href:
                info["socials"].append(href)

        self._crawl_contact_pages(soup, url, info)
        return info

    def _crawl_contact_pages(self, soup: BeautifulSoup, base_url: str, info: Dict):
        contact_keywords = ["contact", "about", "team", "support", "impressum", "imprint"]
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in contact_keywords):
                full_url = urllib.parse.urljoin(base_url, href)
                if urllib.parse.urlparse(full_url).netloc == urllib.parse.urlparse(base_url).netloc:
                    page_html = self.fetch_page(full_url)
                    if page_html:
                        more_emails = self.extract_emails(page_html)
                        for e in more_emails:
                            if e not in info["emails"]:
                                info["emails"].append(e)
                        time.sleep(0.3)
