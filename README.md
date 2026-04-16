#LLM Daily Equity Report

An automated backend pipeline that uses **Generative AI (Anthropic Claude)** to research undervalued small-cap and micro-cap stocks across global markets and delivers daily formatted investment insights directly to your inbox.

---

## 🚀 What It Does

Every day, this system automatically:
1. 🎲 Picks a **random global market or sector** (India, USA, Biotech, Japan, etc.)
2. 🤖 Uses **Claude AI with real-time web search** to find 5 undervalued or distressed stocks with turnaround potential
3. 📧 Delivers a **beautifully formatted HTML email** with stock analysis and source links

---


## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Runtime** | Python 3.12 on AWS Lambda |
| **AI Model** | Anthropic Claude Haiku (claude-haiku-4-5) |
| **AI Capability** | LLM + Real-time Web Search via Claude Tools API |
| **Email Delivery** | AWS Simple Email Service (SES) |
| **Scheduler** | AWS EventBridge (daily cron trigger) |
| **Auth & Security** | AWS IAM roles + environment variable secrets |
| **HTTP** | Python `urllib` (zero dependencies, Lambda-native) |

---

## ✨ Key Features

- **Generative AI Integration** — Uses Anthropic's Claude API with tool use (web search) to retrieve and synthesize live financial data
- **Prompt Engineering** — Structured prompts enforce consistent output format across 20+ global markets and sectors
- **Serverless Architecture** — Fully managed, zero server maintenance, scales automatically
- **HTML Email Rendering** — Markdown-to-HTML pipeline with emoji formatting, clickable links, and responsive layout
- **Secure Secrets Management** — API keys stored as AWS Lambda environment variables, never hardcoded
- **Error Handling & Logging** — Structured exception handling with CloudWatch logging for production reliability
- **Zero Dependencies** — Uses only Python standard library + boto3 (pre-installed on Lambda)

---

## 📬 Sample Output

Each email contains:
- 📈 5 stock picks with company name and ticker
- 🏭 Industry classification
- 📉 Why the stock is underperforming
- 🚀 Catalysts that could trigger a turnaround
- 🔗 Source links from financial news, Substack, Reddit, Seeking Alpha

---

## 🌍 Covered Markets & Sectors

India · USA · Europe · UK · Japan · China · Hong Kong · Australia · Mexico · Global Banks · Technology · Biotech · Metal Industry · Indian Microfinance · Indian SME · USA Microcap · Europe Laggards · Stocks with Insider Buys

---


*Built with Python · AWS Lambda · Anthropic Claude AI · AWS SES*
