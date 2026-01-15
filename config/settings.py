import os
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

if not TELEGRAM_TOKEN or not CHAT_ID:
    # We might want to raise an error or just warn dependent on strictness.
    # For now, we'll let the application handle it if it needs to send a message.
    pass
