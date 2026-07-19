from duckduckgo_search import DDGS
from typing import List, Dict
import time
import re

class SearchAgent:
    def __init__(self):
        self.ddgs = DDGS()

    def search_companies(self, query: str, max_results: int = 20) -> List[Dict[str, str]]:
        results = []
        try:
            for r in self.ddgs.text(query, max_results=max_results):
                results.append({
                    "title": r.get("title", ""),
                    "url": r.get("href", ""),
                    "snippet": r.get("body", ""),
                })
                time.sleep(0.5)
        except:
            pass
        return results

    def build_queries(self, country: str, city: str, category: str, company_size: str = "",
                      search_type: str = "Companies") -> List[str]:
        entity = "companies" if search_type == "Companies" else "universities colleges"
        queries = []

        base_parts = [f"{category} {entity}"]
        if city: base_parts.append(city)
        if country: base_parts.append(country)
        if company_size: base_parts.append(company_size)
        base = " ".join(base_parts)

        queries.append(base)
        queries.append(f"{base} official website")
        queries.append(f"{base} contact")
        queries.append(f"{category} {entity} in {city} {country}")
        queries.append(f"best {category} {entity} {city} {country} 'contact us'")

        if search_type == "Colleges/Universities":
            queries.append(f"{category} {entity} {city} {country} admissions email")
        else:
            queries.append(f"{category} {entity} {city} {country} email address")
            queries.append(f"{category} {entity} {city} {country} -jobs -careers -linkedin")

        return queries
