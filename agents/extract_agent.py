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

COUNTRY_CODES = {
    "afghanistan": "93", "albania": "355", "algeria": "213", "andorra": "376", "angola": "244",
    "argentina": "54", "armenia": "374", "australia": "61", "austria": "43", "azerbaijan": "994",
    "bahrain": "973", "bangladesh": "880", "belarus": "375", "belgium": "32", "bolivia": "591",
    "bosnia": "387", "brazil": "55", "brunei": "673", "bulgaria": "359", "cambodia": "855",
    "canada": "1", "chile": "56", "china": "86", "colombia": "57", "costa rica": "506",
    "croatia": "385", "cyprus": "357", "czech": "420", "denmark": "45", "dominican": "1",
    "ecuador": "593", "egypt": "20", "el salvador": "503", "estonia": "372", "ethiopia": "251",
    "finland": "358", "france": "33", "georgia": "995", "germany": "49", "ghana": "233",
    "greece": "30", "guatemala": "502", "hong kong": "852", "hungary": "36", "iceland": "354",
    "india": "91", "indonesia": "62", "iran": "98", "iraq": "964", "ireland": "353",
    "israel": "972", "italy": "39", "jamaica": "1", "japan": "81", "jordan": "962",
    "kazakhstan": "7", "kenya": "254", "kuwait": "965", "kyrgyzstan": "996", "laos": "856",
    "latvia": "371", "lebanon": "961", "libya": "218", "liechtenstein": "423", "lithuania": "370",
    "luxembourg": "352", "macau": "853", "madagascar": "261", "malaysia": "60", "maldives": "960",
    "malta": "356", "mexico": "52", "moldova": "373", "monaco": "377", "mongolia": "976",
    "montenegro": "382", "morocco": "212", "myanmar": "95", "namibia": "264", "nepal": "977",
    "netherlands": "31", "new zealand": "64", "nicaragua": "505", "nigeria": "234", "north korea": "850",
    "norway": "47", "oman": "968", "pakistan": "92", "palestine": "970", "panama": "507",
    "paraguay": "595", "peru": "51", "philippines": "63", "poland": "48", "portugal": "351",
    "qatar": "974", "romania": "40", "russia": "7", "rwanda": "250", "saudi arabia": "966",
    "senegal": "221", "serbia": "381", "singapore": "65", "slovakia": "421", "slovenia": "386",
    "south africa": "27", "south korea": "82", "spain": "34", "sri lanka": "94", "sudan": "249",
    "sweden": "46", "switzerland": "41", "syria": "963", "taiwan": "886", "tajikistan": "992",
    "tanzania": "255", "thailand": "66", "tunisia": "216", "turkey": "90", "turkmenistan": "993",
    "uganda": "256", "ukraine": "380", "united arab emirates": "971", "uk": "44", "usa": "1",
    "united states": "1", "america": "1", "uruguay": "598", "uzbekistan": "998", "vatican": "39",
    "venezuela": "58", "vietnam": "84", "yemen": "967", "zambia": "260", "zimbabwe": "263",
    "england": "44", "britain": "44", "scotland": "44", "wales": "44",
    "uae": "971", "dubai": "971", "abudhabi": "971",
    "berlin": "49", "munich": "49", "hamburg": "49", "frankfurt": "49",
    "paris": "33", "lyon": "33", "marseille": "33",
    "london": "44", "manchester": "44", "birmingham": "44",
    "new york": "1", "los angeles": "1", "chicago": "1", "san francisco": "1",
    "toronto": "1", "vancouver": "1", "montreal": "1",
    "sydney": "61", "melbourne": "61", "brisbane": "61",
    "bangalore": "91", "mumbai": "91", "delhi": "91", "chennai": "91",
    "dubai": "971", "abudhabi": "971", "sharjah": "971",
    "doha": "974", "riyadh": "966", "jeddah": "966", "mecca": "966",
    "kuala lumpur": "60", "jakarta": "62", "manila": "63", "hanoi": "84", "ho chi minh": "84",
    "tokyo": "81", "osaka": "81", "kyoto": "81", "seoul": "82", "beijing": "86", "shanghai": "86",
}

class ExtractAgent:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    def get_country_code(self, country: str, city: str = "") -> str:
        lookup = f"{city} {country}".lower()
        for key, code in COUNTRY_CODES.items():
            if key in lookup:
                return f"+{code}"
        return ""

    def add_country_code_to_phone(self, phone: str, country: str, city: str = "") -> str:
        if not phone:
            return ""
        phone = phone.strip()
        if phone.startswith("+"):
            return phone
        cc = self.get_country_code(country, city)
        digits = re.sub(r'\D', '', phone)
        if digits.startswith("00"):
            return f"+{digits[2:]}"
        if cc and not digits.startswith(cc.replace("+", "")):
            return f"{cc}{digits}"
        return phone

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

    def extract_company_info(self, url: str, country: str = "", city: str = "") -> Dict:
        info = {"url": url, "name": "", "phone": "", "phone_with_code": "",
                "emails": [], "socials": [], "description": "", "page_text": "",
                "has_contact_page": False}

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
        if phones:
            info["phone"] = phones[0].strip()
            info["phone_with_code"] = self.add_country_code_to_phone(info["phone"], country, city)

        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            if "linkedin.com" in href:
                info["socials"].append(href)
            elif "facebook.com" in href:
                info["socials"].append(href)

        self._crawl_contact_pages(soup, url, info, country, city)
        return info

    def _crawl_contact_pages(self, soup: BeautifulSoup, base_url: str, info: Dict,
                             country: str = "", city: str = ""):
        contact_keywords = ["contact", "about", "team", "support", "impressum", "imprint"]
        for a in soup.find_all("a", href=True):
            href = a.get("href", "")
            text = a.get_text(strip=True).lower()
            if any(kw in text for kw in contact_keywords):
                full_url = urllib.parse.urljoin(base_url, href)
                if urllib.parse.urlparse(full_url).netloc == urllib.parse.urlparse(base_url).netloc:
                    page_html = self.fetch_page(full_url)
                    if page_html:
                        info["has_contact_page"] = True
                        more_emails = self.extract_emails(page_html)
                        for e in more_emails:
                            if e not in info["emails"]:
                                info["emails"].append(e)
                        phones = re.findall(r'[\+\(]?[1-9][0-9 .\-\(\)]{8,}[0-9]', page_html)
                        if phones and not info["phone"]:
                            info["phone"] = phones[0].strip()
                            info["phone_with_code"] = self.add_country_code_to_phone(info["phone"], country, city)
                        time.sleep(0.3)
