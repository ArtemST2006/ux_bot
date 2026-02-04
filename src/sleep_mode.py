from aiogram import Router, F, types
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

router = Router()


# --- Состояния (FSM) ---
class SleepState(StatesGroup):
    choosing_min = State()  # Выбор минимума
    choosing_max = State()  # Выбор максимума
    choosing_method = State()  # Выбор: знаю когда лягу или когда встану
    waiting_bedtime = State()  # Ждем ввода времени отхода ко сну
    waiting_wakeup = State()  # Ждем ввода времени подъема


# --- Клавиатуры ---

def get_hours_kb(prefix: str):
    """Генерирует кнопки с часами (3ч, 4ч ... 12ч)"""
    builder = InlineKeyboardBuilder()
    for i in range(3, 13):
        builder.button(text=f"{i}ч", callback_data=f"{prefix}_{i}")
    builder.adjust(5)
    return builder.as_markup()


def get_method_kb():
    """Кнопки выбора метода расчета"""
    builder = InlineKeyboardBuilder()
    builder.button(text="Я знаю, во сколько лягу", callback_data="method_bedtime")
    builder.button(text="Я знаю, во сколько встану", callback_data="method_wakeup")
    builder.adjust(1)
    return builder.as_markup()


def get_main_menu_kb():
    """Главное меню для выхода"""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="🧘 Практики"), KeyboardButton(text="😴 Контроль сна")],
            [KeyboardButton(text="🔔 Настроить уведомления")]
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите действие..."
    )


# --- Хендлеры (Логика настройки) ---

@router.message(F.text == "😴 Контроль сна")
async def sleep_mode_start(message: types.Message, state: FSMContext):
    text = (
        "Этот помощник поможет рассчитать идеальное время для сна и пробуждения.\n"
        "Мы будем использовать циклы сна по 1.5 часа (90 минут), чтобы ты просыпался бодрым.\n\n"
        "Сначала выбери: сколько часов сна для тебя **минимум**?"
    )
    await message.answer(text, reply_markup=get_hours_kb("min"))
    await state.set_state(SleepState.choosing_min)


@router.callback_query(StateFilter(SleepState.choosing_min), F.data.startswith("min_"))
async def process_min_sleep(callback: types.CallbackQuery, state: FSMContext):
    min_hours = int(callback.data.split("_")[1])
    await state.update_data(min_sleep=min_hours)

    await callback.message.edit_text(
        f"Принято: минимум {min_hours}ч.\n"
        "А сколько часов ты хочешь спать в **идеале (максимум)**?",
        reply_markup=get_hours_kb("max")
    )
    await state.set_state(SleepState.choosing_max)


@router.callback_query(StateFilter(SleepState.choosing_max), F.data.startswith("max_"))
async def process_max_sleep(callback: types.CallbackQuery, state: FSMContext):
    max_hours = int(callback.data.split("_")[1])
    data = await state.get_data()
    min_hours = data.get('min_sleep')

    if min_hours > max_hours:
        await callback.answer("Минимум не может быть больше максимума!", show_alert=True)
        return

    await state.update_data(max_sleep=max_hours)

    text = (
        f"Твои нормы: {min_hours}ч - {max_hours}ч.\n\n"
        "Что будем рассчитывать?"
    )
    await callback.message.edit_text(text, reply_markup=get_method_kb())
    await state.set_state(SleepState.choosing_method)


@router.callback_query(StateFilter(SleepState.choosing_method), F.data == "method_bedtime")
async def ask_bedtime(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text(
        "Во сколько ты планируешь лечь спать?\n"
        "(Напиши время, например: 23:30)\n\n"
        "💡 *Совет:* Обычно человеку нужно около 15 минут, чтобы уснуть. Учти это при вводе времени."
        , parse_mode="Markdown")
    await state.set_state(SleepState.waiting_bedtime)


@router.callback_query(StateFilter(SleepState.choosing_method), F.data == "method_wakeup")
async def ask_wakeup(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Во сколько тебе нужно встать?\n(Напиши время, например: 07:00)")
    await state.set_state(SleepState.waiting_wakeup)


# --- ЛОГИКА РАСЧЕТА ЦИКЛОВ ---

def get_sleep_cycles(base_time: datetime, min_h: int, max_h: int, method: str):
    """
    Рассчитывает варианты времени на основе циклов по 1.5 часа.
    method: 'bedtime' (знаем когда легли, ищем когда встать)
            или 'wakeup' (знаем когда встать, ищем когда лечь)
    """
    cycle_duration = 1.5  # часа
    options = []

    # Проверяем циклы от 1 до 10 (от 1.5 до 15 часов сна)
    for i in range(1, 11):
        sleep_duration = i * cycle_duration

        # Если длительность сна попадает в диапазон (или очень близка к нему)
        # Разрешаем небольшой выход за границы (если диапазон узкий), но в приоритете точное попадание
        if (sleep_duration >= min_h and sleep_duration <= max_h) or \
                (min_h == max_h and abs(sleep_duration - min_h) <= 0.75):

            delta = timedelta(hours=sleep_duration)

            if method == 'bedtime':
                result_time = base_time + delta
            else:
                result_time = base_time - delta

            options.append({
                'cycles': i,
                'hours': sleep_duration,
                'time': result_time.strftime("%H:%M")
            })

    return options


# 6. Расчет (Если знаем, когда ляжем)
@router.message(StateFilter(SleepState.waiting_bedtime))
async def calculate_wakeup_range(message: types.Message, state: FSMContext):
    user_time_str = message.text.strip()

    try:
        base_time = datetime.strptime(user_time_str, "%H:%M")
    except ValueError:
        await message.answer("Неверный формат. Попробуй еще раз (например, 23:00):")
        return

    data = await state.get_data()
    min_h = data['min_sleep']
    max_h = data['max_sleep']

    # Получаем варианты
    options = get_sleep_cycles(base_time, min_h, max_h, method='bedtime')

    if not options:
        # Если ничего не нашли (странный диапазон), берем просто min и max
        delta_min = timedelta(hours=min_h)
        delta_max = timedelta(hours=max_h)
        t_min = (base_time + delta_min).strftime("%H:%M")
        t_max = (base_time + delta_max).strftime("%H:%M")
        response = f"Для заданного диапазона ({min_h}-{max_h}ч) точных циклов нет. Ориентировочно вставай между {t_min} и {t_max}."
    else:
        response = f"🛌 Если лечь в **{user_time_str}**, лучшие варианты для пробуждения:\n\n"
        for opt in options:
            response += f"• **{opt['time']}** (Сон: {opt['hours']}ч — {opt['cycles']} циклов)\n"

        response += "\nПробуждение в конце цикла помогает чувствовать себя бодрым! ☀️"

    await message.answer(response, reply_markup=get_main_menu_kb())
    await state.clear()


# 7. Расчет (Если знаем, когда встать)
@router.message(StateFilter(SleepState.waiting_wakeup))
async def calculate_bedtime_range(message: types.Message, state: FSMContext):
    user_time_str = message.text.strip()

    try:
        base_time = datetime.strptime(user_time_str, "%H:%M")
    except ValueError:
        await message.answer("Неверный формат. Попробуй еще раз (например, 07:00):")
        return

    data = await state.get_data()
    min_h = data['min_sleep']
    max_h = data['max_sleep']

    # Получаем варианты (обратный отсчет)
    options = get_sleep_cycles(base_time, min_h, max_h, method='wakeup')

    # Сортируем варианты по времени (от раннего к позднему), чтобы было красиво
    options.sort(key=lambda x: x['time'])

    if not options:
        # Fallback
        delta_min = timedelta(hours=min_h)
        delta_max = timedelta(hours=max_h)
        t_earliest = (base_time - delta_max).strftime("%H:%M")
        t_latest = (base_time - delta_min).strftime("%H:%M")
        response = f"Для диапазона ({min_h}-{max_h}ч) точных циклов нет. Ложись между {t_earliest} и {t_latest}."
    else:
        response = f"⏰ Чтобы бодро встать в **{user_time_str}**, ложись спать в:\n\n"
        for opt in options:
            response += f"• **{opt['time']}** (Сон: {opt['hours']}ч — {opt['cycles']} циклов)\n"

        response += "\nНе забудь лечь в постель на 15 минут раньше, чтобы успеть уснуть! 😴"

    await message.answer(response, reply_markup=get_main_menu_kb())
    await state.clear()