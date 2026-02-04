# src/practice_list.py

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)

router = Router()

# ======================
# CALLBACKS
# ======================
CB_CATS = "pr:cats"                   # показать типы практик
CB_CAT_PREFIX = "pr:cat:"             # открыть тип pr:cat:<cat>
CB_ITEM_PREFIX = "pr:item:"           # открыть элемент pr:item:<cat>:<item>
CB_HOME = "pr:home"                   # назад в главное меню (reply keyboard)

CB_FAV_ADD_PREFIX = "fav:add:"        # добавить fav:add:<cat>:<item>
CB_FAV_RM_PREFIX = "fav:rm:"          # удалить fav:rm:<cat>:<item>


# ======================
# ДАННЫЕ
# ======================
def bullets(lines: list[str]) -> str:
    return "\n".join([f"• {x}" for x in lines])


CATEGORIES = {
    "exercises": {
        "title": "Упражнения",
        "items": [
            {
                "id": "breathing_gym",
                "title": "Дыхательная гимнастика",
                "text": bullets([
                    "Сделайте медленный глубокий вдох.",
                    "Задержите дыхание на 4–6 секунд.",
                    "Медленно выдохните.",
                    "Повторите цикл 6–8 раз.",
                ]),
            },
            {
                "id": "release_tension",
                "title": "Выплеск напряжения",
                "text": bullets([
                    "Напрягайте мышцы по очереди: от пальцев ног вверх.",
                    "Каждую группу напрягайте 8–10 секунд.",
                    "После этого полностью расслабляйте.",
                    "Закончите на области шеи.",
                ]),
            },
            {
                "id": "protective_circle",
                "title": "Защитный круг",
                "text": bullets([
                    "Большим пальцем правой руки нажмите на центр левой ладони.",
                    "На нажатие — вдох, на ослабление — выдох.",
                    "Повторите 10 раз.",
                    "Сделайте то же самое с другой ладонью.",
                ]),
            },
            {
                "id": "drop_tension",
                "title": "Сброс напряжения",
                "text": bullets([
                    "Сожмите ладонь в кулак (большой палец внутри).",
                    "Сжимая — выдох, разжимая — вдох.",
                    "Повторите 5–6 раз.",
                    "Можно делать с закрытыми глазами.",
                ]),
            },
            {
                "id": "king_kong",
                "title": "Кинг-Конг",
                "text": bullets([
                    "Руки согнуты перед грудью, глаза прикрыты.",
                    "Сожмите кулаки и сильно напрягите мышцы рук.",
                    "Дышите спокойно, удерживайте напряжение 5–10 секунд.",
                    "Полностью расслабьте руки, дайте им свободно опуститься.",
                    "Сделайте медленный вдох и выдох, почувствуйте тепло и тяжесть в руках.",
                    "Можно выполнять незаметно для окружающих.",
                ]),
            },
            {
                "id": "sighs",
                "title": "Вздохи",
                "text": bullets([
                    "Сядьте удобно, руки на бёдрах.",
                    "Сделайте глубокий вдох и короткую задержку.",
                    "Немного наклонитесь вперёд.",
                    "Сделайте один длинный выдох.",
                    "Повторите несколько раз.",
                ]),
            },
            {
                "id": "breath_focus",
                "title": "Концентрация на дыхании",
                "text": bullets([
                    "2–5 минут наблюдайте дыхание: вдох/выдох.",
                    "На вдохе мысленно направляйте дыхание в части тела.",
                    "Сделайте 10 медленных вдохов.",
                    "Про себя: «Я расслаблен».",
                ]),
            },
        ],
    },

    "tips": {
        "title": "Советы",
        "items": [
            {"id": "tip1", "title": "Совет 1", "text": "Перед экзаменом меньше кофеина (кофе/крепкий чай/газировка). Лучше — вода, орехи, фрукты."},
            {"id": "tip2", "title": "Совет 2", "text": "Смех помогает снизить напряжение и улучшить восстановление."},
            {"id": "tip3", "title": "Совет 3", "text": "Любая физическая активность помогает «сжечь» стресс."},
        ],
    },

    "facts": {
        "title": "Интересные факты",
        "items": [
            {"id": "fact1", "title": "Факт 1", "text": "Прогулки на природе связаны с лучшим самочувствием."},
            {"id": "fact2", "title": "Факт 2", "text": "Короткие отвлечения во время умственного труда повышают вероятность ошибок."},
            {"id": "fact3", "title": "Факт 3", "text": "Смартфон перед сном часто ухудшает качество сна."},
            {"id": "fact4", "title": "Факт 4", "text": "Музыка может снижать стресс и поддерживать концентрацию."},
        ],
    },

    "support": {
        "title": "Поддержка",
        "items": [
            {"id": "sup1", "title": "Поддержка 1", "text": "Сейчас тяжело — и это нормально. Давай просто на один шаг."},
            {"id": "sup2", "title": "Поддержка 2", "text": "Ты не обязан(а) справляться идеально. Достаточно — по-человечески."},
            {"id": "sup3", "title": "Поддержка 3", "text": "Сделай паузу. Иногда это самый продуктивный ход."},
        ],
    },
}

# Индекс "cat:item" -> данные
ITEM_INDEX: dict[str, dict] = {}
for cat_id, cat in CATEGORIES.items():
    for item in cat["items"]:
        ITEM_INDEX[f"{cat_id}:{item['id']}"] = {
            "cat_id": cat_id,
            "cat_title": cat["title"],
            "id": item["id"],
            "title": item["title"],
            "text": item["text"],
        }


# ======================
# ИЗБРАННОЕ (in-memory)
# ======================
FAVORITES: dict[int, set[str]] = {}  # user_id -> set({"cat:item", ...})

def fav_key(cat_id: str, item_id: str) -> str:
    return f"{cat_id}:{item_id}"

def user_favs(user_id: int) -> set[str]:
    return FAVORITES.setdefault(user_id, set())

def is_fav(user_id: int, key: str) -> bool:
    return key in user_favs(user_id)


# ======================
# КЛАВИАТУРЫ
# ======================
def kb_categories() -> InlineKeyboardMarkup:
    rows = []
    for cat_id, cat in CATEGORIES.items():
        rows.append([InlineKeyboardButton(text=cat["title"], callback_data=f"{CB_CAT_PREFIX}{cat_id}")])
    rows.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data=CB_HOME)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_category_items(cat_id: str) -> InlineKeyboardMarkup:
    cat = CATEGORIES[cat_id]
    rows = []
    for item in cat["items"]:
        rows.append([InlineKeyboardButton(
            text=item["title"],
            callback_data=f"{CB_ITEM_PREFIX}{cat_id}:{item['id']}"
        )])
    rows.append([InlineKeyboardButton(text="⬅️ Назад к типам", callback_data=CB_CATS)])
    rows.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data=CB_HOME)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def kb_item_actions(user_id: int, cat_id: str, item_id: str, back_to_cat: bool = True) -> InlineKeyboardMarkup:
    key = fav_key(cat_id, item_id)
    rows = []

    # Только тут: добавить/удалить избранное
    if is_fav(user_id, key):
        rows.append([InlineKeyboardButton(text="❌ Удалить из избранного", callback_data=f"{CB_FAV_RM_PREFIX}{cat_id}:{item_id}")])
    else:
        rows.append([InlineKeyboardButton(text="⭐ В избранное", callback_data=f"{CB_FAV_ADD_PREFIX}{cat_id}:{item_id}")])

    # Навигация назад
    if back_to_cat:
        rows.append([InlineKeyboardButton(text="⬅️ Назад к списку", callback_data=f"{CB_CAT_PREFIX}{cat_id}")])
    rows.append([InlineKeyboardButton(text="⬅️ Назад к типам", callback_data=CB_CATS)])
    rows.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data=CB_HOME)])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    kb = [
        [KeyboardButton(text="🧘 Практики"), KeyboardButton(text="⭐ Избранное")],
        [KeyboardButton(text="😴 Контроль сна")],
        [KeyboardButton(text="🔔 Настроить уведомления")],
    ]
    return ReplyKeyboardMarkup(keyboard=kb, resize_keyboard=True, input_field_placeholder="Выберите действие...")


# ======================
# РЕНДЕРЫ
# ======================
async def show_categories(target: Message | CallbackQuery):
    text = "Выберите тип практик:"
    if isinstance(target, Message):
        await target.answer(text, reply_markup=kb_categories())
    else:
        await target.message.edit_text(text, reply_markup=kb_categories())
        await target.answer()


async def show_category(callback: CallbackQuery, cat_id: str):
    cat = CATEGORIES[cat_id]
    await callback.message.edit_text(
        f"**{cat['title']}**\nВыберите пункт:",
        reply_markup=kb_category_items(cat_id),
        parse_mode="Markdown",
    )
    await callback.answer()


async def show_item(callback: CallbackQuery, cat_id: str, item_id: str):
    key = fav_key(cat_id, item_id)
    data = ITEM_INDEX.get(key)
    if not data:
        await callback.answer("Не найдено.", show_alert=True)
        return

    user_id = callback.from_user.id
    text = f"**{data['title']}**\n\n{data['text']}"
    await callback.message.edit_text(
        text,
        reply_markup=kb_item_actions(user_id, cat_id, item_id),
        parse_mode="Markdown",
    )
    await callback.answer()


# ======================
# ПУБЛИЧНЫЕ ФУНКЦИИ ДЛЯ main.py
# ======================
async def show_practice_list_message(message: Message):
    # При нажатии "🧘 Практики" — показываем ТИПЫ
    await show_categories(message)


async def show_favorites_message(message: Message):
    # Кнопка ⭐ Избранное — только из главного меню
    user_id = message.from_user.id
    favs = [k for k in user_favs(user_id) if k in ITEM_INDEX]

    if not favs:
        await message.answer("⭐ Избранное пока пустое. Добавь что-нибудь из практик 🙂")
        return

    # Выдаем список избранного кнопками (без отдельной кнопки 'Избранное' где-то ещё)
    rows = []
    for key in favs:
        d = ITEM_INDEX[key]
        rows.append([InlineKeyboardButton(text=f"{d['title']} — {d['cat_title']}", callback_data=f"{CB_ITEM_PREFIX}{key}")])

    rows.append([InlineKeyboardButton(text="🏠 В главное меню", callback_data=CB_HOME)])

    await message.answer(
        "⭐ **Избранное**\nВыберите пункт:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=rows),
        parse_mode="Markdown"
    )


# ======================
# HANDLERS
# ======================
@router.message(Command("practices"))
async def cmd_practices(message: Message):
    await show_categories(message)


@router.callback_query(F.data == CB_CATS)
async def cb_categories(callback: CallbackQuery):
    await show_categories(callback)


@router.callback_query(F.data.startswith(CB_CAT_PREFIX))
async def cb_open_category(callback: CallbackQuery):
    cat_id = callback.data.replace(CB_CAT_PREFIX, "", 1)
    if cat_id not in CATEGORIES:
        await callback.answer("Категория не найдена.", show_alert=True)
        return
    await show_category(callback, cat_id)


@router.callback_query(F.data.startswith(CB_ITEM_PREFIX))
async def cb_open_item(callback: CallbackQuery):
    payload = callback.data.replace(CB_ITEM_PREFIX, "", 1)  # <cat>:<item>
    if ":" not in payload:
        await callback.answer("Ошибка данных.", show_alert=True)
        return
    cat_id, item_id = payload.split(":", 1)
    if cat_id not in CATEGORIES:
        await callback.answer("Категория не найдена.", show_alert=True)
        return
    await show_item(callback, cat_id, item_id)


@router.callback_query(F.data.startswith(CB_FAV_ADD_PREFIX))
async def cb_fav_add(callback: CallbackQuery):
    payload = callback.data.replace(CB_FAV_ADD_PREFIX, "", 1)  # <cat>:<item>
    if ":" not in payload:
        await callback.answer("Ошибка данных.", show_alert=True)
        return
    cat_id, item_id = payload.split(":", 1)

    key = fav_key(cat_id, item_id)
    data = ITEM_INDEX.get(key)
    if not data:
        await callback.answer("Не найдено.", show_alert=True)
        return

    user_id = callback.from_user.id
    user_favs(user_id).add(key)

    # сообщение + возврат к списку конкретных практик
    await callback.message.answer(f"✅ Добавлено в избранное: {data['title']}")
    await show_category(callback, cat_id)


@router.callback_query(F.data.startswith(CB_FAV_RM_PREFIX))
async def cb_fav_remove(callback: CallbackQuery):
    payload = callback.data.replace(CB_FAV_RM_PREFIX, "", 1)  # <cat>:<item>
    if ":" not in payload:
        await callback.answer("Ошибка данных.", show_alert=True)
        return
    cat_id, item_id = payload.split(":", 1)

    key = fav_key(cat_id, item_id)
    data = ITEM_INDEX.get(key)
    if not data:
        await callback.answer("Не найдено.", show_alert=True)
        return

    user_id = callback.from_user.id
    user_favs(user_id).discard(key)

    await callback.message.answer(f"🗑 Удалено из избранного: {data['title']}")
    await show_category(callback, cat_id)


@router.callback_query(F.data == CB_HOME)
async def cb_home(callback: CallbackQuery):
    # Возвращаем пользователя в главное меню: текст + ReplyKeyboard
    await callback.message.answer("Что ты хочешь сделать?", reply_markup=main_menu_keyboard())
    await callback.answer()
