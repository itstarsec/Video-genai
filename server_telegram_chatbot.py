import asyncio
from flask import Flask, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import threading

TOKEN = "6322621270:AAGapDbnqdVzPn68wQMdcKih3VtA_v1W3nk"
CHAT_ID = "-4677628090"

# Biến toàn cục lưu trạng thái gần nhất
last_status = "Chưa có trạng thái"

# Flask App
app_flask = Flask(__name__)

@app_flask.route('/status-check', methods=['GET'])
def status_check():
    return jsonify({"status": last_status})

# Bot Telegram
async def yes(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_status
    last_status = "yes"
    await context.bot.send_message(chat_id=CHAT_ID, text="Hello")

async def no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global last_status
    last_status = "no"
    await context.bot.send_message(chat_id=CHAT_ID, text="World")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Nhập /yes hoặc /no để nhận phản hồi.")

def run_flask():
    app_flask.run(host="0.0.0.0", port=8888, debug=False)

def main():
    # Khởi chạy Flask trên một luồng riêng
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()

    # Bot Telegram
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("yes", yes))
    app.add_handler(CommandHandler("no", no))

    print("Bot Telegram đang chạy...")
    app.run_polling()

if __name__ == "__main__":
    main()
