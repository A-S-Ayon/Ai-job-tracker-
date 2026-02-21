import httpx
import logging
import os

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# ⚠️ WARNING: Delete these credentials before pushing to GitHub!
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def send_telegram_alert(title: str, company: str, url: str, score: int, summary: str) -> bool:
    """Sends a formatted Markdown message to Telegram via the Bot API."""
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logging.error("Telegram credentials missing. Please set them in the script.")
        return False

    # Formatting the message with Markdown for readability
    message = (
        f"🚨 *High-Value Job Match! (Score: {score}/10)*\n\n"
        f"*Role:* {title}\n"
        f"*Company:* {company}\n"
        f"*Summary:* {summary}\n\n"
        f"[Apply Here]({url})"
    )

    # The Telegram API endpoint for sending messages
    api_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    # We must pass the Chat ID and Text in the payload
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True
    }

    try:
        response = httpx.post(api_url, json=payload, timeout=10.0)
        response.raise_for_status()
        logging.info("Successfully sent Telegram alert!")
        return True
    except httpx.HTTPError as e:
        logging.error(f"Failed to send Telegram message: {e}")
        return False

# --- Testing Block ---
if __name__ == "__main__":
    print("Testing notifier.py...")
    success = send_telegram_alert(
        title="AI Engineer - RAG & Python",
        company="Tech Innovators Inc.",
        url="https://example.com/job/123",
        score=9,
        summary="Build autonomous agents using Python, n8n, and fine-tuned LLMs."
    )
    if success:
        print("Check your Telegram app! The test message should be there.")