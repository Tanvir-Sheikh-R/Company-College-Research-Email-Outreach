from openai import OpenAI
from typing import Dict, List, Optional
import json

SYSTEM_CLASSIFY = """You are a strict company/college validator. Your job is to filter search results and ONLY pass through legitimate company or college websites.

REJECT anything that is:
- Job boards (LinkedIn, Indeed, Glassdoor, etc.)
- News articles, blog posts, press releases
- Directory listing pages (Yellow Pages, company directory pages, etc.)
- Review sites (G2, Capterra, Trustpilot)
- Wikipedia, YouTube, social media pages
- Freelance platforms (Upwork, Fiverr)
- E-commerce product pages
- Anything that lists MANY companies (not a single company site)

ACCEPT only:
- The official website of a single legitimate company/college
- A company's official contact page
- A college/university official website

Be very strict. It's better to reject a borderline result than to pass noise."""

SYSTEM_EXTRACT = """You are a business data extraction expert. Extract structured information from company/college website content.

Rules:
- Only extract data clearly present in the text
- Use "unknown" rather than guessing
- Location should be specific (city, country) if found
- Industry/Category should match what the company actually does
- Company name should be the official registered name"""

class LLMAgent:
    def __init__(self, api_key: str):
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = "deepseek/deepseek-v4-flash:free"

    def expand_search_keywords(self, category: str, search_type: str = "Companies") -> List[str]:
        entity = "companies" if search_type == "Companies" else "colleges, universities, institutes"
        prompt = f"""The user is searching for {entity} in the category: "{category}".

Generate a list of 8-12 related search keywords and titles that would find RELEVANT {entity} similar to or related to "{category}".

For {entity}, think about:
- Related industry fields, sub-categories, specializations
- Alternative terms people might use
- Related course names (for colleges)
- Related service areas (for companies)

Return ONLY a JSON array of strings, nothing else. Example format for "AI":
["Artificial Intelligence", "Machine Learning", "Deep Learning", "Data Science", "AI Solutions", "Intelligent Systems", "Computer Vision", "NLP", "AI Consulting", "Automation"]

Return JSON array:"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
                max_tokens=500,
                temperature=0.3,
            )
            result = json.loads(resp.choices[0].message.content)
            if isinstance(result, list):
                return result
            for v in result.values():
                if isinstance(v, list):
                    return v
            return [category]
        except:
            return [category]

    def classify_search_result(self, title: str, snippet: str, url: str, category: str) -> Dict:
        prompt = f"""You are analyzing a search result for finding "{category}" companies/colleges.

URL: {url}
Title: {title}
Snippet: {snippet[:600]}

Determine:
1. Is this the official website of ONE specific company/college? (not a directory, news, job board)
2. Does it match the category "{category}"?
3. Is it likely a legitimate, operating business/college?

Return JSON:
{{
  "is_valid_target": true/false,
  "reason": "brief explanation why",
  "entity_type": "company" / "college" / "directory" / "news" / "job_board" / "other",
  "confidence": 0.0-1.0,
  "likely_name": "the company/college name if identifiable"
}}"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_CLASSIFY},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=250,
                temperature=0.1,
            )
            return json.loads(resp.choices[0].message.content)
        except:
            return {"is_valid_target": True, "reason": "llm_fallback", "entity_type": "unknown", "confidence": 0.3, "likely_name": ""}

    def extract_company_details(self, page_text: str, url: str) -> Dict:
        prompt = f"""Extract structured company/college information from this website content.

URL: {url}
Content:
{page_text[:2500]}

Return JSON with these fields (use "unknown" if not found):
{{
  "name": "official name",
  "industry": "what they do",
  "location": "address or location mentioned",
  "phone": "contact phone number",
  "email": "contact email found in text",
  "description": "brief 1-sentence description",
  "has_physical_address": true/false,
  "about_text": "key about-us text"
}}"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": SYSTEM_EXTRACT},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=350,
                temperature=0.1,
            )
            return json.loads(resp.choices[0].message.content)
        except:
            return {"name": "", "industry": "", "location": "", "phone": "", "email": "", "description": "", "has_physical_address": False, "about_text": ""}

    def extract_company_name(self, html_title: str, url: str, page_text: str = "") -> str:
        prompt = f"""Extract the real company/organization name from this website.
Title: {html_title}
URL: {url}
Content: {page_text[:500] if page_text else 'N/A'}

Return ONLY the clean official company name, nothing else."""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.1,
            )
            return resp.choices[0].message.content.strip().strip('"')
        except:
            return html_title

    def generate_outreach_email(self, company_name: str, email: str, category: str,
                                 country: str, city: str, sender_name: str,
                                 sender_company: str, custom_message: str = "",
                                 company_description: str = "") -> str:
        context = f" Context about them: {company_description}" if company_description else ""
        prompt = f"""Write a professional business outreach email.

From: {sender_name}, {sender_company}
To: {company_name} ({email})
Context: Reaching out about partnership/proposal in {category} sector, {city}, {country}.{context}
Additional instructions: {custom_message if custom_message else 'None'}

Write a concise, professional email (max 150 words). 
- First line must be "Subject: [your subject]"
- Personalize it — show you've done research on them
- Clear call to action
- Warm but professional tone"""

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=500,
                temperature=0.7,
            )
            return resp.choices[0].message.content.strip()
        except:
            return f"Subject: Partnership Opportunity\n\nDear Team at {company_name},\n\n{custom_message if custom_message else 'I would like to discuss a potential partnership opportunity.'}\n\nBest regards,\n{sender_name}"
