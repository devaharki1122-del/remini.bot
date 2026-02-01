import replicate
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ContextTypes, CallbackQueryHandler
)

# ====== SETTINGS ======
BOT_TOKEN = "8231599662:AAFxtG4i1OHLAEIVcRGy6P0yIopqj3T1_fU"
REPLICATE_API_KEY = "r8_OR9q5BvZ6E2ZbHD3njW8PRegnOEYrgL4WxDgA"
ADMIN_ID = 8186735286

CHANNELS = ["@chanaly_boot", "@team_988"]

GFPGAN = "tencentarc/gfpgan:0fbacf7afc6c144e5be9767cff80f25aff23e52b0708f17e20f9879b2f21516c"

replicate_client = replicate.Client(api_token=REPLICATE_API_KEY)

users = set()
bot_enabled = True

# ====== FORCE JOIN ======
async def force_join(update, context):
    user_id = update.effective_user.id
    for ch in CHANNELS:
        member = await context.bot.get_chat_member(ch, user_id)
        if member.status in ["left", "kicked"]:
            kb = [
                [InlineKeyboardButton("📢 Join Channel 1", url="https://t.me/chanaly_boot")],
                [InlineKeyboardButton("📢 Join Channel 2", url="https://t.me/team_988")]
            ]
            await update.message.reply_text(
                "جوین بکە بەم کەناڵانە 👇",
                reply_markup=InlineKeyboardMarkup(kb)
            )
            return False
    return True

# ====== START ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_enabled:
        return

    if not await force_join(update, context):
        return

    users.add(update.effective_user.id)

    kb = [
        [InlineKeyboardButton("🖼️ جوانکردنی وێنە", callback_data="img")],
        [InlineKeyboardButton("🎥 جوانکردنی ڤیدیۆ", callback_data="vid")]
    ]
    await update.message.reply_text(
        "🤖 بەخێربێیت بۆ AI Enhancer Bot",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ====== ADMIN PANEL ======
async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    kb = [
        [InlineKeyboardButton("👥 Users", callback_data="users")],
        [InlineKeyboardButton("📢 Broadcast", callback_data="broadcast")],
        [InlineKeyboardButton("🔴 Close Bot", callback_data="close")],
        [InlineKeyboardButton("🟢 Open Bot", callback_data="open")]
    ]
    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=InlineKeyboardMarkup(kb)
    )

# ====== BUTTONS ======
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global bot_enabled
    query = update.callback_query
    await query.answer()

    if query.data == "users":
        await query.message.reply_text(f"👥 Users: {len(users)}")

    elif query.data == "broadcast":
        context.user_data["broadcast"] = True
        await query.message.reply_text("✍️ نامەکەت بنێرە بۆ ناردن بۆ هەموو")

    elif query.data == "close":
        bot_enabled = False
        await query.message.reply_text("🔴 بوت داخرا")

    elif query.data == "open":
        bot_enabled = True
        await query.message.reply_text("🟢 بوت کراوە")

    elif query.data == "img":
        await query.message.reply_text("📷 وێنە بنێرە")

    elif query.data == "vid":
        await query.message.reply_text("🎥 ڤیدیۆ بنێرە")

# ====== BROADCAST ======
async def broadcast_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("broadcast"):
        for u in users:
            try:
                await context.bot.send_message(u, update.message.text)
            except:
                pass
        context.user_data["broadcast"] = False
        await update.message.reply_text("✅ نێردرا")

# ====== AI IMAGE ======
def enhance(image_url):
    try:
        return replicate_client.run(GFPGAN, input={"img": image_url})
    except:
        return replicate_client.run(
            "nightmareai/real-esrgan",
            input={"image": image_url, "scale": 4}
        )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_enabled:
        return

    if not await force_join(update, context):
        return

    file = await update.message.photo[-1].get_file()
    result = enhance(file.file_path)

    await context.bot.send_photo(ADMIN_ID, result)
    await update.message.reply_text("✅ نێردرا بۆ ئەدمین")

# ====== VIDEO ======
async def video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not bot_enabled:
        return

    await context.bot.send_video(ADMIN_ID, update.message.video.file_id)
    await update.message.reply_text("🎥 نێردرا بۆ ئەدمین")

# ====== RUN ======
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("admin", admin_panel))
app.add_handler(CallbackQueryHandler(buttons))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, broadcast_msg))
app.add_handler(MessageHandler(filters.PHOTO, photo))
app.add_handler(MessageHandler(filters.VIDEO, video))

app.run_polling()