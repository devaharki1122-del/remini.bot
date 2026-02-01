import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# ===== TOKENS IN CODE =====
BOT_TOKEN = "8231599662:AAERL7v8r2TmITuql6P6Bf4I729qlzedNE"
REPLICATE_API_TOKEN = "r8_OR9q5BvZ6E2ZbHD3njW8PRegnOEYrgL4WxDgA"

logging.basicConfig(level=logging.INFO)

# ===== START MENU =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🖼 جوانکردنی وێنە 4K", callback_data="photo")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("بەخێربێیت 🤖\nوێنە بنێرە بۆ جوانکردن:", reply_markup=reply_markup)

# ===== BUTTON =====
async def buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.message.reply_text("وێنە بنێرە 📸")

# ===== REPLICATE FUNCTION =====
def enhance_image(image_url):
    url = "https://api.replicate.com/v1/predictions"
    headers = {
        "Authorization": f"Token {REPLICATE_API_TOKEN}",
        "Content-Type": "application/json"
    }
    data = {
        "version": "42fed1c4977a9b8f60c9c0d3d7d8b6b6e8b5b5f5a5a5a5a5a5a5a5a5a5a5a5a",  # real-esrgan
        "input": {
            "image": image_url,
            "scale": 4
        }
    }

    response = requests.post(url, json=data, headers=headers)
    prediction = response.json()

    # wait for result
    get_url = prediction["urls"]["get"]
    while True:
        r = requests.get(get_url, headers=headers).json()
        if r["status"] == "succeeded":
            return r["output"]
        elif r["status"] == "failed":
            return None

# ===== PHOTO HANDLER =====
async def photo_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("⏳ چاوەڕێبە... وێنەکەت 4K دەکرێت")

    photo = update.message.photo[-1]
    file = await photo.get_file()
    image_url = file.file_path

    result = enhance_image(image_url)

    if result:
        await update.message.reply_photo(result)
    else:
        await update.message.reply_text("هەڵەیەک ڕوویدا ❌")

# ===== MAIN =====
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.PHOTO, photo_handler))
    app.add_handler(MessageHandler(filters.ALL, buttons))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()