from duckduckgo_search import DDGS
from typing import List, Dict, Optional
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
                      search_type: str = "Companies", expanded_keywords: Optional[List[str]] = None) -> List[str]:
        entity = "companies" if search_type == "Companies" else "universities colleges"
        queries = []

        keywords = [category]
        if expanded_keywords:
            keywords.extend(expanded_keywords)
        keywords = list(set(keywords))[:6]

        for kw in keywords:
            parts = [f"{kw} {entity}"]
            if city: parts.append(city)
            if country: parts.append(country)
            if company_size: parts.append(company_size)
            base = " ".join(parts)

            queries.append(base)
            queries.append(f"{base} official website")
            queries.append(f"{base} contact email")
            queries.append(f"{kw} {entity} in {city} {country}")
            queries.append(f"{kw} {entity} {city} -jobs -careers -linkedin")

            if search_type == "Colleges/Universities":
                queries.append(f"{kw} {entity} {city} {country} admissions")
            else:
                queries.append(f"{kw} {entity} {city} {country} contact")
                queries.append(f"{kw} company {city} {country} email")

        return list(set(queries))
