# 🤖 AI-Powered Job Opportunity Tracker

An intelligent, automated job-hunting pipeline that scrapes live job listings, uses AI to evaluate and score them against a target skill set, and instantly sends a Telegram notification for every high-value match — so you never miss a relevant opportunity.

---

## 📋 Table of Contents

- [Overview](#overview)
- [How It Works](#how-it-works)
- [Project Structure](#project-structure)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [Database Schema](#database-schema)
- [Example Telegram Alert](#example-telegram-alert)
- [Contributing](#contributing)
- [License](#license)

---

## Overview

This project automates the tedious process of job searching. It:

1. **Scrapes** job listings from Hacker News Jobs (with pagination support) using a headless browser.
2. **Evaluates** each job with an LLM (via the Groq API) against a Data/AI Engineer's skill profile.
3. **Filters** out recruiting agencies and low-relevance listings.
4. **Notifies** you via Telegram with a rich, formatted alert for every strong match (score ≥ 5/10).
5. **Remembers** processed jobs in a local SQLite database to avoid duplicate processing across runs.

---

## How It Works

```
[Hacker News Jobs Page]
         │
         ▼
  ┌─────────────┐
  │  scraper.py │  ← Playwright headless browser, pagination-aware
  └──────┬──────┘
         │  List of job dicts
         ▼
  ┌─────────────┐
  │    db.py    │  ← Check if job_url already exists in SQLite
  └──────┬──────┘
         │  New jobs only
         ▼
  ┌──────────────┐
  │ evaluator.py │  ← Groq LLM (llama-3.3-70b-versatile) scores the job
  └──────┬───────┘
         │  { score, summary, is_agency }
         ▼
  ┌──────────────┐
  │  notifier.py │  ← Sends Telegram alert if score ≥ 5 AND not agency
  └──────┬───────┘
         │
         ▼
  ┌─────────────┐
  │    db.py    │  ← Save job + score + summary to SQLite
  └─────────────┘
```

---

## Project Structure

```
Ai-job-tracker-/
│
├── main.py          # Orchestrator — runs the full pipeline end-to-end
├── scraper.py       # Playwright-based web scraper with pagination
├── evaluator.py     # Groq LLM integration for AI-powered job scoring
├── notifier.py      # Telegram Bot API integration for real-time alerts
├── db.py            # SQLite database layer (init, read, write)
├── jobs.db          # Auto-generated SQLite database (do not commit)
├── .gitignore       # Git ignore rules
└── .github/         # GitHub Actions / config files
```

---

## Tech Stack

| Component        | Technology                         |
|------------------|------------------------------------|
| Language         | Python 3.10+                       |
| Web Scraping     | [Playwright](https://playwright.dev/python/) (headless Chromium) |
| AI Evaluation    | [Groq API](https://groq.com/) — `llama-3.3-70b-versatile` |
| Notifications    | [Telegram Bot API](https://core.telegram.org/bots/api) via `httpx` |
| Database         | SQLite (`jobs.db`)                 |
| HTTP Client      | `httpx`                            |

---

## Prerequisites

- Python **3.10** or higher
- A **[Groq API Key](https://console.groq.com/)** (free tier available)
- A **Telegram Bot Token** — create one via [@BotFather](https://t.me/BotFather)
- Your **Telegram Chat ID** — get it from [@userinfobot](https://t.me/userinfobot)

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/A-S-Ayon/Ai-job-tracker-.git
   cd Ai-job-tracker-
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate        # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install playwright groq httpx
   ```

4. **Install Playwright's Chromium browser:**
   ```bash
   playwright install chromium
   ```

---

## Configuration

The tracker uses **environment variables** for all credentials. **Never hardcode secrets in source files.**

Set the following environment variables in your shell or a `.env` file:

```bash
export GROQ_API_KEY="your_groq_api_key_here"
export TELEGRAM_BOT_TOKEN="your_telegram_bot_token_here"
export TELEGRAM_CHAT_ID="your_telegram_chat_id_here"
```

> 💡 On Windows, use `set` instead of `export`.

> ⚠️ **Security Warning:** Never commit your API keys or tokens to version control. Ensure `jobs.db` and any `.env` files are listed in `.gitignore`.

---

## Usage

### Run the full pipeline

```bash
python main.py
```

This will:
- Initialize the SQLite database (if not already created)
- Scrape up to **15** jobs from [Hacker News Jobs](https://news.ycombinator.com/jobs)
- Evaluate each new job with the Groq LLM
- Send Telegram alerts for matches scoring **≥ 5/10** that are **not** recruiting agencies
- Save all results to the local database

### Run individual modules for testing

```bash
# Test the scraper
python scraper.py

# Test the AI evaluator
python evaluator.py

# Test the Telegram notifier
python notifier.py

# Test the database layer
python db.py
```

### Adjust the job limit

In `main.py`, change the `max_jobs` parameter:
```python
jobs = scraper.scrape_jobs(TARGET_URL, max_jobs=50)
```

---

## Database Schema

Jobs are persisted in a local SQLite database (`jobs.db`) with the following schema:

| Column           | Type     | Description                                      |
|------------------|----------|--------------------------------------------------|
| `id`             | INTEGER  | Auto-incremented primary key                     |
| `job_url`        | TEXT     | Unique job URL (used to detect duplicates)       |
| `title`          | TEXT     | Job title                                        |
| `company`        | TEXT     | Company name                                     |
| `raw_description`| TEXT     | Raw job description text                         |
| `llm_score`      | INTEGER  | AI relevance score (1–10)                        |
| `is_agency`      | BOOLEAN  | Whether the poster is a recruiting agency        |
| `summary`        | TEXT     | One-sentence AI-generated summary                |
| `processed_date` | TEXT     | UTC timestamp of when the job was processed      |

---

## Example Telegram Alert

When a strong match is found, you receive a message like this in Telegram:

```
🚨 High-Value Job Match! (Score: 8/10)

Role: AI Engineer - RAG & Python
Company: Tech Innovators Inc.
Summary: Build autonomous agents using Python, n8n, and fine-tuned LLMs.

[Apply Here](https://news.ycombinator.com/item?id=...)
```

---

## Contributing

Contributions are welcome! Here are some ideas for improvements:

- [ ] Add support for more job boards (LinkedIn, Indeed, Wellfound)
- [ ] Build a web dashboard to view scored jobs
- [ ] Add email notification support
- [ ] Dockerize the project for easy deployment
- [ ] Schedule automated runs with GitHub Actions or a cron job
- [ ] Make the candidate skill profile configurable via a config file

To contribute:
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/your-feature`)
3. Commit your changes (`git commit -m 'Add your feature'`)
4. Push to your branch (`git push origin feature/your-feature`)
5. Open a Pull Request

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with ❤️ by [A-S-Ayon](https://github.com/A-S-Ayon)*
