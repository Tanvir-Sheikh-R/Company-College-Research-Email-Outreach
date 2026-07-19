from ddgs import DDGS
from typing import List, Dict, Optional
import time

class SearchAgent:
    def __init__(self):
        self.ddgs = DDGS()
        self.searched_urls = set()

    def search_companies(self, query: str, max_results: int = 15) -> List[Dict[str, str]]:
        results = []
        try:
            for r in self.ddgs.text(query, max_results=max_results):
                url = r.get("href", "")
                if url and url not in self.searched_urls:
                    self.searched_urls.add(url)
                    results.append({
                        "title": r.get("title", ""),
                        "url": url,
                        "snippet": r.get("body", ""),
                    })
                time.sleep(0.3)
        except:
            pass
        return results

    def reset_dedup(self):
        self.searched_urls = set()

    def build_queries(self, country: str, city: str, category: str,
                      company_size: str = "", search_type: str = "Companies",
                      expanded_keywords: Optional[List[str]] = None,
                      llm_queries: Optional[List[str]] = None) -> List[str]:
        self.reset_dedup()

        entity = "company" if search_type == "Companies" else "college university institute school"
        entity_plural = "companies" if search_type == "Companies" else "colleges universities"

        keywords = [category]
        if expanded_keywords:
            keywords.extend(expanded_keywords)
        keywords = keywords[:12]

        queries = []

        for kw in keywords:
            kw_base = f"{kw} {entity} {city} {country}".strip()

            patterns = [
                kw_base,
                f"{kw} {entity_plural} in {city} {country}",
                f"{kw} {entity} {city} contact email",
                f"top {kw} {entity_plural} {city}",
                f"\"{kw}\" \"{city}\" \"{country}\"",
                f"{kw} {entity} based in {city}",
                f"{city} {kw} {entity}",
                f"{kw} {entity} \"@\" {city}",
            ]

            if search_type == "Companies":
                patterns.extend([
                    f"{kw} {entity_plural} {city} gmbh OR ltd OR inc OR llc",
                    f"list of {kw} {entity_plural} in {city}",
                    f"{kw} company {country} email",
                    f"{kw} {entity_plural} near {city}",
                    f"{kw} {entity} \"contact\" {city}",
                ])
                if company_size:
                    patterns.append(f"{kw} {entity} {city} {company_size}")
            else:
                patterns.extend([
                    f"{kw} course {city} {country}",
                    f"study {kw} in {city} {country}",
                    f"{kw} program college {city}",
                    f"best {kw} colleges in {city} admissions",
                    f"{kw} degree {city} university",
                ])

            queries.extend(patterns)

        queries.append(f"{entity_plural} in {city} {country}")
        queries.append(f"{entity_plural} {country} {category}")
        queries.append(f"{category} \"contact us\" {city}")
        queries.append(f"list of {entity_plural} {city} {country}")
        queries.append(f"{category} {city} email")

        if llm_queries:
            queries.extend(llm_queries)

        queries = list(set(q.strip() for q in queries if q.strip()))
        return queries

    def aggressive_search(self, country: str, city: str, category: str,
                          company_size: str = "", search_type: str = "Companies",
                          expanded_keywords: Optional[List[str]] = None,
                          llm_queries: Optional[List[str]] = None) -> List[Dict[str, str]]:
        queries = self.build_queries(country, city, category, company_size,
                                      search_type, expanded_keywords, llm_queries)
        all_results = []

        for query in queries:
            try:
                results = self.search_companies(query, max_results=10)
                all_results.extend(results)
            except:
                pass

        seen = set()
        unique = []
        for r in all_results:
            if r["url"] not in seen:
                seen.add(r["url"])
                unique.append(r)

        return unique
