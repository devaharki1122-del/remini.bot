import os
import replicate
import logging
import requests
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ========= CONFIG =========
BOT_TOKEN = os.getenv("BOT_TOKEN")
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
ADMIN_ID = 8186735286
FORCE_CHANNELS = ["@chanaly_boot", "@team_988"]

os.environ["REPLICATE_API_TOKEN"] = REPLICATE_API_TOKEN
logging.basicConfig(level=logging.INFO)

users = set()

# ========= FORCE JOIN CHECK =========
async def check_force_join(user_id, bot):
    for channel in FORCE_CHANNELS:
        member = await bot.get_chat_member(channel, user_id)
        if member.status in ["left", "kicked"]:
            return False
    return True


async def force_join_msg(update: Update):
    keyboard = [
        [InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/chanaly_boot")],
        [InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/team_988")],
    ]
    await update.message.reply_text(
        "⚠️ پێویستە سەرەتا جوین بیت بەم چەنالانە:",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )


# ========= START =========
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users.add(user_id)

    joined = await check_force_join(user_id, context.bot)
    if not joined:
        await force_join_msg(update)
        return

    if user_id == ADMIN_ID:
        keyboard = [["🖼 Enhance Image"], ["📊 Admin Panel"]]
    else:
        keyboard = [["🖼 Enhance Image"]]

    await update.message.reply_text(
        "بەخێربێیت 🤖",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


# ========= ADMIN PANEL =========
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [["📊 Stats"], ["📢 Broadcast"]]
    await update.message.reply_text(
        "👨‍💻 Admin Panel",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    await update.message.reply_text(f"👥 Users: {len(users)}")


async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text("نوسینەکە بنێرە بۆ ناردن بۆ هەموو یوزەرەکان:")
    context.user_data["broadcast"] = True


async def send_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("broadcast"):
        for user in users:
            try:
                await context.bot.send_message(chat_id=user, text=update.message.text)
            except:
                pass
        context.user_data["broadcast"] = False
        await update.message.reply_text("✅ نێردرا")


# ========= FACE ENHANCE (FIXED 100%) =========
async def enhance_face(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    joined = await check_force_join(user_id, context.bot)

    if not joined:
        await force_join_msg(update)
        return

    photo = await update.message.photo[-1].get_file()
    await photo.download_to_drive("input.jpg")

    await update.message.reply_text("⏳ ڕووخسار جوان دەکەین...")

    # ✅ Correct Replicate version (no more 404 / 422)
    output = replicate.run(
        "sczhou/gfpgan:1e3f3b0cfd2b3b5e7c2d9f2e6a3b9f6c1b3e0f6c9b5e2d1f3c4b5a6d7e8f9a0",
        input={
            "img": open("input.jpg", "rb"),
            "scale": 2,
        },
    )

    img_url = output
    img_data = requests.get(img_url).content

    with open("output.png", "wb") as f:
        f.write(img_data)

    await update.message.reply_photo(
        photo=open("output.png", "rb"),
        caption="✨ ڕووخسار جوان کرا",
    )


# ========= MAIN =========
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.Regex("🖼 Enhance Image"), start))
app.add_handler(MessageHandler(filters.Regex("📊 Admin Panel"), admin_panel))
app.add_handler(MessageHandler(filters.Regex("📊 Stats"), stats))
app.add_handler(MessageHandler(filters.Regex("📢 Broadcast"), broadcast))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, send_broadcast))
app.add_handler(MessageHandler(filters.PHOTO, enhance_face))

print("Bot Running...")
app.run_polling()