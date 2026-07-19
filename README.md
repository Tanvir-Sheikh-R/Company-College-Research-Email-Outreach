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

## Prerequisites

- Python 3.14+
- A free [OpenRouter](https://openrouter.ai) API key
- A Gmail / Outlook account with an App Password (for sending emails)

## Setup Guide

### 1. Get Your OpenRouter API Key

1. Go to [openrouter.ai/keys](https://openrouter.ai/keys)
2. Sign up for a free account (no credit card required)
3. Click **"Create Key"** and copy the generated key
4. The free tier includes `deepseek/deepseek-v4-flash:free` — unlimited usage

### 2. SMTP Setup (for sending emails)

**Gmail:**
1. Go to your [Google Account](https://myaccount.google.com/security)
2. Enable **2-Step Verification** (required for App Passwords)
3. Go to **Security → App Passwords**
4. Select **Mail** as the app and **Windows Computer** as the device
5. Copy the generated 16-character App Password
6. Use this password in the SMTP settings in the app

| Setting | Value |
|---------|-------|
| SMTP Server | `smtp.gmail.com` |
| SMTP Port | `587` |
| Email | Your full Gmail address |
| Password | The 16-character App Password |

**Outlook / Hotmail:**
| Setting | Value |
|---------|-------|
| SMTP Server | `smtp-mail.outlook.com` |
| SMTP Port | `587` |
| Email | Your full Outlook address |
| Password | Your Microsoft account password (or App Password if 2FA is on) |

> **Note:** SMTP is only needed if you want to send emails from **Tab 3**. Email verification (Tab 1) works without any credentials.

### 3. Installation

```bash
# Clone the repo
git clone https://github.com/your-username/your-repo.git
cd your-repo

# Create virtual environment
python -m venv .venv
.venv\Scripts\activate  # Windows
# source .venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file in the project root:

```env
OPENROUTER_API_KEY=sk-or-v1-your-actual-key-here
```

### 5. Run

```bash
streamlit run app.py
```

## Usage Guide

### Tab 1 — Research
1. Enter OpenRouter API key in the sidebar (or it auto-loads from `.env`)
2. Select **Companies** or **Colleges/Universities**
3. Fill in country, city, category (e.g. "AI", "Software", "Medical")
4. Click **Start Research**
5. The AI will: search → classify → extract emails → verify via SMTP
6. Download results as CSV

### Tab 2 — AI Outreach Drafts
1. Enter your name, agency name, and email
2. Select which companies to generate drafts for
3. Click **Generate Email Drafts**
4. Review and edit drafts before sending

### Tab 3 — Send Emails
1. Enter SMTP credentials (see setup above)
2. Select which drafts to send
3. Click **Send Selected Emails**
4. Delivery results are shown in real-time

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
├── requirements.txt
└── README.md
```

## Free Tier Limitations

| Service | Limitation | Mitigation |
|---------|-----------|------------|
| DeepSeek V4 (OpenRouter) | Rate-limited on free tier | Works fine for research-scale usage |
| DuckDuckGo Search | ~20 results/query | Multiple queries run per search |
| SMTP Email Verification | From your IP, may get rate-limited | Cloudflare Workers for IP rotation (optional) |
| Gmail SMTP Sending | 500 emails/day free | Sufficient for outreach campaigns |

## Contributing

Contributions, issues, and feature requests are welcome!

- 🐛 **Found a bug?** [Open an issue](https://github.com/your-username/your-repo/issues)
- 💡 **Have an idea?** [Start a discussion](https://github.com/your-username/your-repo/discussions)
- 🔧 **Want to contribute?** Fork the repo and submit a pull request

> Replace `your-username/your-repo` with your actual GitHub repository URL.

## License

MIT
