import logging
import os
import http.server
import socketserver
import threading
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Settings ---
TOKEN = '8512047741:AAGpAQ66GKS8V_8eXBQ9g7U__UYUXUZGpaw'
CHANNEL_ID = '@MinecraftMyanmarMCM'

# Render အတွက် Port Error မတက်အောင် Web Server အသေးစားလေး လုပ်ပေးခြင်း
def run_web_server():
    port = int(os.environ.get("PORT", 8000))
    handler = http.server.SimpleHTTPRequestHandler
    # အောက်က စာကြောင်းက Render ကို ငါတို့ Bot အသက်ရှင်နေပါတယ်လို့ အချက်ပြတာပါ
    with socketserver.TCPServer(("", port), handler) as httpd:
        print(f"Serving at port {port}")
        httpd.serve_forever()

async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        keyboard = [[InlineKeyboardButton("Join ရန်နှိပ်ပါ", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Channel အရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\n(Join ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ)",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        "Welcome ပါဗျ။\nBot ကိုစတင်အသုံးပြုနိုင်ပါပြီ။\n\n📜 ရရှိနိုင်သော File များစာရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပါ။\n📖 Bot အသုံးပြုနည်းကြည့်ရန် /tutorial ကိုနှိပ်ပါ။"
    )

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return
    
    file_list = (
        "ရရှိနိုင်သော File များစာရင်း -\n\n"
        "1. Actions and Stuff 1.10\n"
        "2. Item Physics & More\n"
        "3. MM Standard UI V1\n\n"
        "File ရယူရန် အပေါ်က အမည်အတိုင်း တိကျစွာ ရိုက်ပို့ပေးပါ။"
    )
    await update.message.reply_text(file_list)

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide_text = (
        "Advance File Bot အသုံးပြုနည်း Tutorial\n\n"
        "/list ကိုနှိပ်ပြီး ရရှိနိုင်မည့် File စာရင်းများကိုကြည့်ရှုနိုင်ပါသည်။\n"
        "File ရယူလိုပါက ရရှိနိုင်မည့် File ရဲ့ Name ကိုတိကျစွာရိုက်ပို့ပေးရပါမယ် (List ထဲမှာပါတဲ့ File အမည်အတိုင်းပဲဖြစ်ရပါမယ်)။\n"
        "Owner နဲ့ဆက်သွယ်ရန် - @umcrafter_bot"
    )
    await update.message.reply_text(guide_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return

    text = update.message.text.strip()
    
    # --- File Database (ဒီနေရာမှာ သင့်ရဲ့ File ID တွေကို ထည့်ပါ) ---
    file_database = {
        "Actions and Stuff 1.10": "FILE_ID_HERE",
        "Item Physics & More": "FILE_ID_HERE",
        "MM Standard UI V1": "FILE_ID_HERE"
    }

    if text in file_database:
        file_id = file_database[text]
        if file_id == "FILE_ID_HERE":
            await update.message.reply_text("ဒီဖိုင်အတွက် ID မထည့်ရသေးပါဘူးဗျာ။")
        else:
            try:
                await update.message.reply_document(document=file_id)
            except Exception as e:
                await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("တောင်းပန်ပါတယ်၊ အဲ့ဒီအမည်နဲ့ File မရှိသေးပါဘူး။ /list ကိုနှိပ်ပြီး အမည်ကို ပြန်စစ်ပေးပါ။")

def main():
    # Web server ကို background thread နဲ့ run မယ်
    threading.Thread(target=run_web_server, daemon=True).start()

    # Telegram Bot ကို စမယ်
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_files))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    application.run_polling()

if __name__ == '__main__':
    main()
