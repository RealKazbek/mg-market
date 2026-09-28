"""Telegram-бот (aiogram 3).

  /start   — спрашивает язык (Русский/English), запоминает его и показывает
             приветствие + WebApp-кнопку «Открыть магазин» (открывает TMA)
  /orders  — список заказов пользователя (через внутренний API backend)

Выбранный язык становится основным: бот сохраняет его в backend (для своих
сообщений/уведомлений) и пробрасывает в мини-аппку через ?lang=<ru|en>.

Уведомления об оплате шлёт сам backend (через Telegram Bot API), боту ничего
ловить не нужно — он только обрабатывает команды.

Запуск:
    python bot.py
"""
import asyncio
import logging
import os
import sys

import httpx
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    BotCommand,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    WebAppInfo,
)
from dotenv import load_dotenv

load_dotenv()

# Python 3.9 + uvloop does not expose a default loop during module import.
# aiogram's Dispatcher creates one eagerly, so provide it explicitly.
if sys.version_info < (3, 10):
    asyncio.set_event_loop(asyncio.new_event_loop())

BOT_TOKEN = os.getenv("BOT_TOKEN", "")
MINIAPP_URL = os.getenv("MINIAPP_URL", "")
BOT_API_URL = os.getenv("BOT_API_URL", "http://127.0.0.1:8000")
INTERNAL_SECRET = os.getenv("INTERNAL_SECRET", "")

# Локализация статусов заказа.
STATUS_LABELS = {
    "kk": {
        "new": "🆕 Төлем күтілуде", "paid": "✅ Төленді", "shipped": "📦 Жолда",
        "done": "🎉 Аяқталды", "canceled": "❌ Бас тартылды",
    },
    "ru": {
        "new": "🆕 Ожидает оплаты",
        "paid": "✅ Оплачен",
        "shipped": "📦 Отправлен",
        "done": "🎉 Завершён",
        "canceled": "❌ Отменён",
    },
    "en": {
        "new": "🆕 Awaiting payment",
        "paid": "✅ Paid",
        "shipped": "📦 Shipped",
        "done": "🎉 Completed",
        "canceled": "❌ Canceled",
    },
}

# Тексты сообщений бота.
TEXTS = {
    "kk": {
        "choose_lang": "👋 Қош келдіңіз!\n\nДүкенді қай тілде пайдаланғыңыз келетінін таңдаңыз.",
        "no_miniapp": "Дүкен әзірге қолжетімсіз. Кейінірек қайталап көріңіз.",
        "open_shop": "🛍 Дүкенді ашу",
        "welcome": "👋 Дүкенімізге қош келдіңіз!\n\nTelegram ішінде тауарларды қарап, тапсырыс беріп және сатып алуларыңызды бақылай аласыз.",
        "orders_off": "Тапсырыстар әзірге қолжетімсіз.", "orders_err": "Тапсырыстарды жүктеу мүмкін болмады. Кейінірек қайталап көріңіз.",
        "orders_empty": "Әзірге тапсырыстарыңыз жоқ. Дүкенді /start арқылы ашыңыз.", "orders_title": "<b>Тапсырыстарыңыз:</b>",
    },
    "ru": {
        "choose_lang": "Выберите язык / Choose your language:",
        "no_miniapp": (
            "Привет! 🎁 Магазин почти готов, но не задан адрес мини-аппки.\n\n"
            "Запустите ./tgshop.sh build (при активном ngrok) — он сам пропишет "
            "MINIAPP_URL, либо задайте его вручную: ./tgshop.sh miniapp <https-url>. "
            "Затем перезапустите бота (./tgshop.sh dev)."
        ),
        "open_shop": "🛍 Открыть MG Market",
        "welcome": (
            "👋 Добро пожаловать в MG Market!\n\n"
            "Откройте магазин, выберите товары и оформите заказ прямо в Telegram."
        ),
        "orders_off": "Список заказов недоступен: сервер не настроен.",
        "orders_err": "Не удалось получить заказы. Попробуйте позже.",
        "orders_empty": "У вас пока нет заказов. Откройте магазин через /start.",
        "orders_title": "<b>Ваши заказы:</b>",
    },
    "en": {
        "choose_lang": "Choose your language / Выберите язык:",
        "no_miniapp": (
            "Hi! 🎁 The shop is almost ready, but the mini-app URL is not set.\n\n"
            "Run ./tgshop.sh build (with ngrok active) — it will set MINIAPP_URL "
            "automatically, or set it manually: ./tgshop.sh miniapp <https-url>. "
            "Then restart the bot (./tgshop.sh dev)."
        ),
        "open_shop": "🛍 Open MG Market",
        "welcome": (
            "👋 Welcome to MG Market!\n\n"
            "Browse products and place orders directly inside Telegram."
        ),
        "orders_off": "Orders are unavailable: the server is not configured.",
        "orders_err": "Couldn't fetch your orders. Please try again later.",
        "orders_empty": "You have no orders yet. Open the shop via /start.",
        "orders_title": "<b>Your orders:</b>",
    },
}

BUTTONS = {
    "kk": {"store":"🛍 Дүкенді ашу", "orders":"📦 Тапсырыстарым", "cart":"🛒 Себет", "language":"🌐 Тіл", "currency":"💱 Валюта", "help":"ℹ️ Көмек", "choose_currency":"💱 Валютаны таңдаңыз", "settings":"⚙️ Баптаулар"},
    "ru": {"store":"🛍 Открыть MG Market", "orders":"📦 Мои заказы", "cart":"🛒 Корзина", "language":"🌐 Язык", "currency":"💱 Валюта", "help":"ℹ️ Помощь", "choose_currency":"💱 Выберите валюту", "settings":"⚙️ Настройки"},
    "en": {"store":"🛍 Open MG Market", "orders":"📦 My orders", "cart":"🛒 Cart", "language":"🌐 Language", "currency":"💱 Currency", "help":"ℹ️ Help", "choose_currency":"💱 Choose currency", "settings":"⚙️ Settings"},
}


def _norm(code: str) -> str:
    """language_code -> 'ru' | 'en' (пустота / ru* -> 'ru')."""
    code = (code or "").lower()
    if code.startswith("kk") or code.startswith("kaz"):
        return "kk"
    return "ru" if not code or code.startswith("ru") else "en"


def _tg_lang(message: Message) -> str:
    """Язык из Telegram language_code как фоллбэк."""
    code = ""
    if message.from_user and message.from_user.language_code:
        code = message.from_user.language_code
    return _norm(code)


def _webapp_url(lang: str) -> str:
    """MINIAPP_URL с проброшенным ?lang=<ru|en> для мини-аппки."""
    sep = "&" if "?" in MINIAPP_URL else "?"
    return f"{MINIAPP_URL}{sep}lang={lang}"


def _webapp_url_for(lang: str, startapp: str) -> str:
    base = _webapp_url(lang)
    sep = "&" if "?" in base else "?"
    return f"{base}{sep}startapp={startapp}"


def _lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🇰🇿 Қазақша", callback_data="lang:kk"),
                InlineKeyboardButton(
                    text="🇷🇺 Русский", callback_data="lang:ru"
                ),
                InlineKeyboardButton(
                    text="🇬🇧 English", callback_data="lang:en"
                ),
            ]
        ]
    )


def _shop_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=TEXTS[lang]["open_shop"],
                    web_app=WebAppInfo(url=_webapp_url(lang)),
                )
            ]
        ]
    )


def _shortcut_keyboard(lang: str, startapp: str, label: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(
            text=label,
            web_app=WebAppInfo(url=_webapp_url_for(lang, startapp)),
        )
    ]])


def _main_keyboard(lang: str) -> ReplyKeyboardMarkup:
    b = BUTTONS[lang]
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=b["store"], web_app=WebAppInfo(url=_webapp_url(lang)))],
            [KeyboardButton(text=b["orders"]), KeyboardButton(text=b["cart"])],
            [KeyboardButton(text=b["language"]), KeyboardButton(text=b["currency"])],
            [KeyboardButton(text=b["help"])],
        ], resize_keyboard=True, is_persistent=True,
    )


def _welcome_inline(lang: str) -> InlineKeyboardMarkup:
    b = BUTTONS[lang]
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=b["store"], web_app=WebAppInfo(url=_webapp_url(lang)))],
        [InlineKeyboardButton(text="🔥 " + ("Танымал" if lang == "kk" else "Популярное" if lang == "ru" else "Popular"), callback_data="shop:popular")],
        [InlineKeyboardButton(text=b["orders"], callback_data="nav:orders"), InlineKeyboardButton(text=b["settings"], callback_data="nav:settings")],
    ])


def _popular_inline(lang: str) -> InlineKeyboardMarkup:
    label = "🔥 Танымал" if lang == "kk" else "🔥 Популярное" if lang == "ru" else "🔥 Popular"
    return _shortcut_keyboard(lang, "popular", label)


def _currency_keyboard(lang: str, selected: str = "KZT") -> InlineKeyboardMarkup:
    labels = {"KZT": "₸ KZT", "RUB": "₽ RUB", "USD": "$ USD"}
    return InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text=("✅ " if selected == c else "") + labels[c], callback_data=f"currency:{c}") for c in ("KZT", "RUB", "USD")]])


async def _save_lang(user_id: int, lang: str) -> None:
    """Сохранить выбранный язык в backend (для уведомлений/сообщений)."""
    if not INTERNAL_SECRET:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(
                f"{BOT_API_URL}/api/internal/user-lang",
                headers={"X-Internal-Secret": INTERNAL_SECRET},
                json={"user_tg_id": user_id, "lang": lang},
            )
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning(
            "Не удалось сохранить язык пользователя %s: %s", user_id, exc
        )


async def _save_currency(user_id: int, currency: str) -> None:
    if not INTERNAL_SECRET:
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            await client.post(f"{BOT_API_URL}/api/internal/user-currency", headers={"X-Internal-Secret": INTERNAL_SECRET}, json={"user_tg_id": user_id, "currency": currency})
    except Exception as exc:
        logging.getLogger(__name__).warning("Не удалось сохранить валюту пользователя %s: %s", user_id, exc)


async def _stored_lang(user_id: int, fallback: str) -> str:
    """Сохранённый выбор языка из backend; иначе — fallback."""
    if not INTERNAL_SECRET:
        return fallback
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BOT_API_URL}/api/internal/user-lang/{user_id}",
                headers={"X-Internal-Secret": INTERNAL_SECRET},
            )
            resp.raise_for_status()
            lang = resp.json().get("lang")
            if lang in ("kk", "ru", "en"):
                return lang
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning(
            "Не удалось получить язык пользователя %s из backend: %s", user_id, exc
        )
    return fallback


dp = Dispatcher()


@dp.message(CommandStart())
async def cmd_start(message: Message) -> None:
    lang = _tg_lang(message)
    await message.answer(TEXTS[lang]["choose_lang"], reply_markup=_lang_keyboard())


@dp.callback_query(F.data.startswith("lang:"))
async def on_lang(callback: CallbackQuery) -> None:
    selected = callback.data.split(":", 1)[1]
    lang = selected if selected in ("kk", "ru", "en") else "ru"
    t = TEXTS[lang]
    await _save_lang(callback.from_user.id, lang)
    if not MINIAPP_URL.startswith("https://"):
        await callback.message.edit_text(t["no_miniapp"])
    else:
        await callback.message.edit_text(t["welcome"], reply_markup=_welcome_inline(lang))
        await callback.message.answer("MG Market", reply_markup=_main_keyboard(lang))
    await callback.answer()


@dp.message(F.text.in_({BUTTONS["ru"]["currency"], BUTTONS["kk"]["currency"], BUTTONS["en"]["currency"]}))
async def currency_menu(message: Message) -> None:
    lang = await _stored_lang(message.from_user.id, _tg_lang(message))
    await message.answer(BUTTONS[lang]["choose_currency"], reply_markup=_currency_keyboard(lang))


@dp.callback_query(F.data.startswith("currency:"))
async def on_currency(callback: CallbackQuery) -> None:
    code = callback.data.split(":", 1)[1]
    if code not in ("KZT", "RUB", "USD"):
        await callback.answer("Unknown currency", show_alert=True)
        return
    lang = await _stored_lang(callback.from_user.id, _tg_lang(callback.message))
    await _save_currency(callback.from_user.id, code)
    await callback.message.edit_text(BUTTONS[lang]["choose_currency"], reply_markup=_currency_keyboard(lang, code))
    await callback.answer(f"{code} ✓")


@dp.message(F.text.in_({BUTTONS["ru"]["language"], BUTTONS["kk"]["language"], BUTTONS["en"]["language"]}))
async def language_menu(message: Message) -> None:
    await message.answer("🌐 Выберите язык / Тілді таңдаңыз / Choose language", reply_markup=_lang_keyboard())


@dp.message(F.text.in_({BUTTONS["ru"]["cart"], BUTTONS["kk"]["cart"], BUTTONS["en"]["cart"]}))
async def cart_menu(message: Message) -> None:
    lang = await _stored_lang(message.from_user.id, _tg_lang(message))
    await message.answer("🛒 " + ("Откройте корзину в MG Market." if lang == "ru" else "MG Market ішінен себетті ашыңыз." if lang == "kk" else "Open your cart in MG Market."), reply_markup=_shop_keyboard(lang))


@dp.message(F.text.in_({BUTTONS["ru"]["help"], BUTTONS["kk"]["help"], BUTTONS["en"]["help"]}))
async def help_menu(message: Message) -> None:
    lang = await _stored_lang(message.from_user.id, _tg_lang(message))
    help_text = {"ru":"ℹ️ MG Market\n\nЧерез бота можно открыть магазин, изменить язык и валюту, а также посмотреть заказы.","kk":"ℹ️ MG Market\n\nБот арқылы дүкенді ашып, тіл мен валютаны өзгертіп, тапсырыстарды көруге болады.","en":"ℹ️ MG Market\n\nUse the bot to open the store, change language or currency, and view your orders."}[lang]
    await message.answer(help_text, reply_markup=_welcome_inline(lang))


async def _orders_for_user(message: Message, user_id: int) -> None:
    lang = await _stored_lang(user_id, _tg_lang(message))
    t = TEXTS[lang]
    if not INTERNAL_SECRET:
        await message.answer(t["orders_off"])
        return
    try:
        async with httpx.AsyncClient(timeout=10) as client:
            resp = await client.get(
                f"{BOT_API_URL}/api/internal/orders/{user_id}",
                headers={"X-Internal-Secret": INTERNAL_SECRET},
            )
            resp.raise_for_status()
            orders = resp.json()
    except Exception as exc:  # noqa: BLE001
        logging.getLogger(__name__).warning("Order lookup failed for Telegram user %s: %s", user_id, exc)
        await message.answer(t["orders_err"])
        return

    if not orders:
        await message.answer(t["orders_empty"])
        return

    labels = STATUS_LABELS[lang]
    lines = [t["orders_title"], ""]
    for order in orders:
        total = order["total_kopecks"] / 100
        label = labels.get(order["status"], order["status"])
        no = "№" if lang == "ru" else "#"
        lines.append(f"{no}{order['id']} — {label} — {total:,.0f} ₸".replace(",", " "))
    await message.answer("\n".join(lines), reply_markup=_shortcut_keyboard(lang, "orders", "📦 " + ("Тапсырыстарды ашу" if lang == "kk" else "Открыть заказы" if lang == "ru" else "Open orders")))


@dp.message(Command("orders"))
async def cmd_orders(message: Message) -> None:
    await _orders_for_user(message, message.from_user.id)


@dp.message(F.text.in_({BUTTONS["ru"]["orders"], BUTTONS["kk"]["orders"], BUTTONS["en"]["orders"]}))
async def orders_menu(message: Message) -> None:
    await _orders_for_user(message, message.from_user.id)


@dp.message(Command("shop"))
async def cmd_shop(message: Message) -> None:
    lang = await _stored_lang(message.from_user.id, _tg_lang(message))
    await message.answer(TEXTS[lang]["welcome"], reply_markup=_welcome_inline(lang))


@dp.message(Command("cart"))
async def cmd_cart(message: Message) -> None:
    await cart_menu(message)


@dp.message(Command("settings"))
async def cmd_settings(message: Message) -> None:
    lang = await _stored_lang(message.from_user.id, _tg_lang(message))
    await message.answer(BUTTONS[lang]["settings"], reply_markup=InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=BUTTONS[lang]["language"], callback_data="settings:language")],
        [InlineKeyboardButton(text=BUTTONS[lang]["currency"], callback_data="settings:currency")],
    ]))


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    await help_menu(message)


@dp.callback_query(F.data == "nav:orders")
async def inline_orders(callback: CallbackQuery) -> None:
    await callback.answer()
    await _orders_for_user(callback.message, callback.from_user.id)


@dp.callback_query(F.data == "shop:popular")
async def inline_popular(callback: CallbackQuery) -> None:
    lang = await _stored_lang(callback.from_user.id, _tg_lang(callback.message))
    await callback.message.edit_text(
        "🔥 " + ("Танымал тауарлар" if lang == "kk" else "Популярные товары" if lang == "ru" else "Popular products"),
        reply_markup=_popular_inline(lang),
    )
    await callback.answer()


@dp.callback_query(F.data == "nav:settings")
async def inline_settings(callback: CallbackQuery) -> None:
    await callback.answer()
    await cmd_settings(callback.message)


@dp.callback_query(F.data == "settings:currency")
async def inline_settings_currency(callback: CallbackQuery) -> None:
    lang = await _stored_lang(callback.from_user.id, _tg_lang(callback.message))
    await callback.message.edit_text(BUTTONS[lang]["choose_currency"], reply_markup=_currency_keyboard(lang))
    await callback.answer()


@dp.callback_query(F.data == "settings:language")
async def inline_settings_language(callback: CallbackQuery) -> None:
    await callback.message.edit_text("🌐 Выберите язык / Тілді таңдаңыз / Choose language", reply_markup=_lang_keyboard())
    await callback.answer()


async def main() -> None:
    logging.basicConfig(level=logging.INFO)
    if not BOT_TOKEN:
        raise SystemExit("BOT_TOKEN не задан в .env")
    bot = Bot(
        BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    await bot.set_my_commands([
        BotCommand(command="start", description="Open MG Market"),
        BotCommand(command="shop", description="Open the store"),
        BotCommand(command="orders", description="My orders"),
        BotCommand(command="cart", description="Open cart"),
        BotCommand(command="settings", description="Language and currency"),
        BotCommand(command="help", description="Help"),
    ])
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
