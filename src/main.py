import asyncio
import logging
from src.config import config

from aiogram import Bot, Dispatcher
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

from src.notification_settings import router as notifications_router
from src.sleep_mode import router as sleep_router
from src.scheduler import scheduler

dp = Dispatcher()

dp.include_router(notifications_router)
dp.include_router(sleep_router)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = [
        [
            KeyboardButton(text="🧘 Практики"),
            KeyboardButton(text="😴 Контроль сна")
        ],
        [
            KeyboardButton(text="🔔 Настроить уведомления")
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

    greeting_text = (
        "Добро пожаловать! В этом боте можно попробовать практики, "
        "которые помогают успокоиться, воспользоваться помощником по контролю сна, "
        "а также выбрать любимую практику и настроить уведомления для Регулярного выполнения.\n\n"
        "Что ты хочешь сделать?"
    )

    await message.answer(greeting_text, reply_markup=keyboard)


async def main():
    logging.basicConfig(level=logging.INFO)

    bot = Bot(token=config.BOT_TOKEN)

    await bot.delete_webhook(drop_pending_updates=True)

    scheduler.start()

    print("Бот запущен...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        if not config.BOT_TOKEN:
            print("Ошибка: Не указан токен бота!")
        else:
            asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот остановлен")