import asyncio
import logging
from src.config import config

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton

# Импорты наших модулей
from src.practice_list import router as practice_router, show_practice_list_message, show_favorites_message
from src.notification_settings import router as notifications_router
from src.sleep_mode import router as sleep_router
from src.scheduler import scheduler

dp = Dispatcher()

# Подключаем роутеры
dp.include_router(practice_router)
dp.include_router(notifications_router)
dp.include_router(sleep_router)

@dp.message(CommandStart())
async def cmd_start(message: Message):
    kb = [
        [
            KeyboardButton(text="🧘 Практики"),
            KeyboardButton(text="⭐️ Избранное")
        ],
        [
            KeyboardButton(text="😴 Контроль сна"),
            KeyboardButton(text="🔔 Настроить уведомления")
        ]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb,
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

    greeting_text = (
        "Привет 👋\n\n"
        "Это бот с короткими практиками, которые помогают успокоиться, чуть выдохнуть и лучше восстановиться — "
        "особенно в период учёбы, дедлайнов и сессии.\n\n"
        "Тебе доступны следующие разделы:\n\n"
        "🧘 <b>Практики</b>\n"
        "Здесь собраны короткие практики, которые можно использовать в моменты стресса или усталости. "
        "Выбери любую — бот покажет инструкцию, и ты сможешь сразу попробовать.\n\n"
        "⭐️ <b>Избранное</b>\n"
        "Сюда можно добавить практики, которые тебе особенно подошли, чтобы всегда иметь их под рукой.\n\n"
        "⏰ <b>Уведомления</b>\n"
        "Напоминания помогают не забывать про практики — особенно в загруженные дни. "
        "Ты можешь выбрать удобное время или вообще отключить напоминания.\n\n"
        "🌙 <b>Контроль сна</b>\n"
        "Помощник, который подскажет, во сколько лучше лечь или встать, если сложно принять решение из-за усталости или тревоги. "
        "Помогает быстро подобрать подходящее время сна или пробуждения, чтобы ты чувствовал(а) себя чуть более восстановленным(ой)."
    )

    await message.answer(greeting_text, reply_markup=keyboard, parse_mode="HTML")

# --- ОБРАБОТЧИКИ КНОПОК ---

@dp.message(F.text == "🧘 Практики")
async def open_practices(message: Message):
    await show_practice_list_message(message)

@dp.message(F.text == "⭐️ Избранное")
async def open_favorites(message: Message):
    await show_favorites_message(message)

# --------------------------

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