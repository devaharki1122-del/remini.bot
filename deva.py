from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import openai, speech_recognition as sr
from pydub import AudioSegment
import os

# ========== CONFIG ==========
BOT_TOKEN = "8255597665:AAHGs-7xHckM96XmzmaF_qwhj8SjG87EIN8"
API_ID = 32052427
API_HASH = "d9e14b1e99ac33e20d41479a47d2622f"
OPENAI_API_KEY = "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"

openai.api_key = OPENAI_API_KEY

ADMINS = [8186735286]

app = Client("voice_gpt_bot", bot_token=BOT_TOKEN, api_id=API_ID, api_hash=API_HASH)

# ========== BUTTONS ==========
def buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 بوتی تیکتۆک", url="https://t.me/Tiktok_112_bot")],
        [InlineKeyboardButton("👤 نامە بۆ خاوەن بوت", url="https://t.me/Deva_harki")],
        [InlineKeyboardButton("🟢 جەنالی 1", url="https://t.me/chanaly_boot")],
        [InlineKeyboardButton("🟢 جەنالی 2", url="https://t.me/team_988")]
    ])

# ========== GPT ==========
async def gpt(text):
    r = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "وەکو مرۆڤ، زیرەک، دۆستانە و ڕوون وەڵام بدە"},
            {"role": "user", "content": text}
        ],
        temperature=0.8,
        max_tokens=500
    )
    return r.choices[0].message.content

# ========== TEXT ==========
@app.on_message(filters.text)
async def text_handler(c, m):
    reply = await gpt(m.text)
    await m.reply_text(reply, reply_markup=buttons())

# ========== VOICE ==========
@app.on_message(filters.voice)
async def voice_handler(c, m):
    voice_file = await m.download()
    sound = AudioSegment.from_ogg(voice_file)
    wav_path = voice_file.replace(".ogg", ".wav")
    sound.export(wav_path, format="wav")

    r = sr.Recognizer()
    with sr.AudioFile(wav_path) as source:
        audio = r.record(source)
        text = r.recognize_google(audio, language="ar")

    reply = await gpt(text)
    await m.reply_text(reply, reply_markup=buttons())

    os.remove(voice_file)
    os.remove(wav_path)

# ========== PHOTO ==========
@app.on_message(filters.photo)
async def photo_handler(c, m):
    reply = await gpt("ئەم وێنەیە وەکو مرۆڤ باسی بکە")
    await m.reply_text(reply, reply_markup=buttons())

# ========== ADMIN PANEL ==========
@app.on_message(filters.user(ADMINS) & filters.command("admin"))
async def admin(c, m):
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 ستاتس", callback_data="stats")],
        [InlineKeyboardButton("🔒 Force Join", url="https://t.me/chanaly_boot")]
    ])
    await m.reply_text("⚡ ئەدمین پانیل", reply_markup=kb)

print("🤖 BOT RUNNING...")
app.run()