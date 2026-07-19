# 🔍 Company & College Research + Email Outreach

[![Streamlit App](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)](https://company-college-research.streamlit.app)

An AI-powered multi-agent system that searches for companies or colleges by country, city, category, and size — then scrapes contact info, verifies emails via SMTP, generates personalized outreach drafts using DeepSeek V4, and sends them directly from the browser.

## Features

- **🔎 Smart Search** — DuckDuckGo search with AI classification to filter only legitimate company/college websites
- **📧 Email Extraction** — Scrapes contact/about/impressum pages for emails
- **✅ SMTP Verification** — DNS MX check + SMTP handshake to validate emails (filters personal & disposable domains)
- **🧠 AI Validation** — DeepSeek V4 (free via OpenRouter) classifies results, extracts company details, and filters noise
- **✍️ AI Outreach Drafts** — Generates personalized business proposals for each company
- **📤 Email Sending** — Send drafts directly via SMTP (Gmail, Outlook, etc.)
- **📥 CSV Export** — Download verified results as CSV

## Tech Stack

| Component | Tool |
|-----------|------|
| UI | Streamlit |
| LLM | DeepSeek V4 Flash (free via OpenRouter) |
| Search | DuckDuckGo (free, no API key) |
| Scraping | httpx + BeautifulSoup |
| Email Verification | dnspython + smtplib (free SMTP handshake) |
| Email Sending | smtplib with TLS |

## Quick Start

1. **Clone & install**
   ```bash
   pip install -r requirements.txt
   ```

2. **Add your API key**
   Edit `.env`:
   ```
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   ```
   Get a free key at [openrouter.ai/keys](https://openrouter.ai/keys)

3. **Run**
   ```bash
   streamlit run app.py
   ```

## Usage

1. Enter your OpenRouter API key (or set in `.env`)
2. Fill in search criteria (country, city, category)
3. Click **Start Research** — AI filters and extracts contacts
4. Verify emails automatically
5. Generate AI outreach drafts in Tab 2
6. Send emails via SMTP in Tab 3

## Free Tier

Everything runs on free services:
- **DeepSeek V4 Flash** — free via OpenRouter
- **DuckDuckGo** — unlimited free search
- **Email verification** — self-hosted SMTP (free)
- **Email sending** — use Gmail/Outlook free tier

## Project Structure

```
├── app.py                  # Main Streamlit application
├── agents/
│   ├── search_agent.py     # Web search & query building
│   ├── extract_agent.py    # Website scraping & email extraction
│   ├── verify_agent.py     # SMTP email verification
│   ├── llm_agent.py        # DeepSeek V4 integration (classification + drafting)
│   └── email_sender.py     # SMTP email sender
├── templates/
│   └── email_template.txt
├── .env                    # API key configuration
└── requirements.txt
```

## License

MIT
