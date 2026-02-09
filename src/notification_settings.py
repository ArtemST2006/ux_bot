from aiogram import Router, F, types
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

from src.scheduler import schedule_job

router = Router()

def get_time_kb():
    builder = InlineKeyboardBuilder()
    for hour in range(7, 23):
        time_text = f"{hour:02d}:00"
        builder.button(text=time_text, callback_data=f"notify_time_{time_text}")
    builder.adjust(4)
    return builder.as_markup()


def get_yes_no_kb():
    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data="notify_add_more")
    builder.button(text="Нет", callback_data="notify_finish")
    builder.adjust(2)
    return builder.as_markup()


def get_main_menu_kb():
    """Возвращает главное меню (С ИСПРАВЛЕНИЕМ: добавлена кнопка Избранное)"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧘 Практики"), KeyboardButton(text="⭐️ Избранное")],
            [KeyboardButton(text="😴 Контроль сна"), KeyboardButton(text="🔔 Настроить уведомления")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )

@router.message(F.text == "🔔 Настроить уведомления")
async def settings_start(message: types.Message):
    await message.answer(
        "Выбери время, в которое бот будет напоминать о практике:",
        reply_markup=get_time_kb()
    )


@router.callback_query(F.data.startswith("notify_time_"))
async def time_selected(callback: types.CallbackQuery):
    selected_time = callback.data.split("_")[-1]

    schedule_job(callback.bot, callback.from_user.id, selected_time)

    await callback.answer(f"Установлено: {selected_time}")

    await callback.message.edit_text(
        f"Время уведомлений <b>{selected_time}</b> задано.\nХочешь получать уведомления еще в какое-то время?",
        reply_markup=get_yes_no_kb(),
        parse_mode="HTML"
    )


@router.callback_query(F.data == "notify_add_more")
async def want_more(callback: types.CallbackQuery):
    await callback.message.edit_text(
        "Хорошо, выбери еще одно время:",
        reply_markup=get_time_kb()
    )


@router.callback_query(F.data == "notify_finish")
async def finish(callback: types.CallbackQuery):
    await callback.message.delete()
    await callback.message.answer(
        "Настройки уведомлений сохранены! Я напомню тебе о практике.",
        reply_markup=get_main_menu_kb()
    )