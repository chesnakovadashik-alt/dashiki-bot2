import logging
import json
import os
from datetime import datetime, date
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

import os
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 1011500220

DATA_FILE = "users.json"

COUPONS = {
    "kiss_hot": {"name": "Жоски горячи поцелуй", "description": "Самый горячий в зубы наху"},
    "sleeping": {"name": "Сладко спим вместе", "description": "Можем что-нибудь посмотреть на твой вкус, жоск поболтать и лечь спать вместе"},
    "to_suck_off_1": {"name": "Отсос обычный", "description": "Классический"},
    "to_suck_off_2": {"name": "Отсос жоски слюнявый", "description": "Жоска, сочно, по маслу наху"},
    "to_suck_off_3": {"name": "Отсос нежный", "description": "Нежно, аккуратно, со вкусом, как говорится"},
}

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# ---------- Работа с файлом ----------

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f)

user_coupons = load_data()


# ---------- Команда /start ----------

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if str(user.id) not in user_coupons:
        user_coupons[str(user.id)] = {
            "name": user.first_name,
            "last_used": None
        }
        save_data(user_coupons)

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🎉 Новый пользователь: {user.first_name}"
        )

    await update.message.reply_text(
        f"Саламалекум наху, {user.first_name}! ✨\n\n"
        f"С 23 февраля, мушчински! Долго думала, чем тебя удивить эдаким и порадовать, чего тебе точно еще не делали, материальное называть ты не захотел, кроме вонючего глока, поэтому дарю тебе символический невиданный аттракцион щедрости. Все уведомления с заданием приходят мне во время нажатия кнопочек тобой.\n"
        f"В день можно использовать только 1 возможность, сильно не балдеем да тоже"
    )

    await show_coupons(update, context)


# ---------- Показ кнопок ----------

async def show_coupons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []

    for key, coupon in COUPONS.items():
        keyboard.append([
            InlineKeyboardButton(
                coupon["name"],
                callback_data=f"use_{key}"
            )
        ])

    markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_text(
            "Ну раздавай бля проститутка",
            reply_markup=markup
        )
    else:
        await update.message.reply_text(
            "Ну раздавай бля проститутка",
            reply_markup=markup
        )


# ---------- Обработка кнопок ----------

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user = query.from_user
    user_id = str(user.id)
    today = str(date.today())

    last_used = user_coupons[user_id].get("last_used")

    if last_used == today:
        await query.edit_message_text(
            "😈не ахуеваем, уже использовал сегодня возможность!\n"
            "Приходи завтра"
        )
        return

    key = query.data.replace("use_", "")
    coupon = COUPONS[key]

    user_coupons[user_id]["last_used"] = today
    save_data(user_coupons)

    await query.edit_message_text(
        f"Да ты че, базара нет, вохможность активирована\n\n"
        f"{coupon['name']}\n"
        f"{coupon['description']}\n\n"
        f"На сегодня все, не ахуеваем особо, в тонусе"
    )

    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=f"🔔 Активирована возможность:\n{coupon['name']}"
    )


# ---------- Запуск ----------

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_callback))

    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()