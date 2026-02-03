import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Конфигурация бота"""

    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")

    @classmethod
    def validate(cls):
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN не установлен в .env файле")

        if ":" not in cls.BOT_TOKEN:
            raise ValueError(f"Неверный формат токена: {cls.BOT_TOKEN}")

        return True


config = Config()