from apscheduler.schedulers.asyncio import AsyncIOScheduler
from aiogram import Bot

# Создаем глобальный объект планировщика
scheduler = AsyncIOScheduler()


async def send_reminder(bot: Bot, chat_id: int):
    """Функция, которая отправляет само сообщение"""
    try:
        await bot.send_message(
            chat_id=chat_id,
            text="🧘 Напоминание! Пришло время уделить пару минут практике."
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление пользователю {chat_id}: {e}")


def schedule_job(bot: Bot, chat_id: int, time_str: str):
    """Добавляет задачу в расписание"""
    hour, minute = map(int, time_str.split(':'))

    scheduler.add_job(
        send_reminder,
        trigger='cron',
        hour=hour,
        minute=minute,
        args=[bot, chat_id],
        id=f"reminder_{chat_id}_{time_str}",
        replace_existing=True
    )