import requests
import logging
from config.settings import TELEGRAM_TOKEN, CHAT_ID

logger = logging.getLogger("skyscraper.notifications")

class TelegramNotifier:
    def __init__(self, token=TELEGRAM_TOKEN, chat_id=CHAT_ID):
        self.token = token
        self.chat_id = chat_id
        if not self.token or not self.chat_id:
            logger.warning("Telegram credentials not found. Notifications will be disabled.")

    def send_message(self, message: str):
        """
        Sends a message to the configured Telegram chat.
        """
        if not self.token or not self.chat_id:
            logger.info(f"Mock Notification (Telegram not configured): {message}")
            return

        url = f"https://api.telegram.org/bot{self.token}/sendMessage"
        payload = {
            "chat_id": self.chat_id,
            "text": message
        }

        try:
            response = requests.post(url, json=payload, timeout=10)
            response.raise_for_status()
            logger.info("Notification sent successfully.")
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram notification: {e}")
