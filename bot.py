import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (Render Port Error ကျော်ရန်) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online and Running!"

def run():
    # Render ရဲ့ Dynamic Port ကို ဖမ်းယူခြင်း
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.start()

# --- 2. Bot Settings ---
TOKEN = '8512047741:AAGpAQ6GGKS8V_8eXBQ9g7U__UYUXUZGpbw'
CHANNEL_ID = '@MinecraftMyanmarMCM'

# --- 3. Bot Logic ---

# Channel Join မ Join စစ်ဆေးခြင်း
async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        keyboard = [[InlineKeyboardButton("Join ရန်နှိပ်ပါ", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Channel အရင်​Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ\n\nJoin ပြီးပါက /start ကို ပြန်နှိပ်ပါ။",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        "Welcome ပါဗျ Advance File Bot ကိုစတင်အသုံးပြုနိုင်ပါပြီ။\n\nရယူနိုင်သော File များစာရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပါ\Advance File Bot အသုံးပြုနည်းကြည့်ရန် /tutorial ကိုနှိပ်ပါ"
    )

# /list command
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return
    
    file_list = (
        "ရယူနိုင်သော File များစာရင်း -\n\n"
        "MC Last Version\n\n"
        "1. Actions and Stuff 1.10\n"
        "2. Item Physics & More\n"
        "3. MM Standard UI V1\n\n"
        "4. RealismCraft 2.4\n\n"
        "5. Naturalist 26.1\n\n"
        "6. RLCraft Bedrock Edition 1.2\n\n"
        "7. Better on Bedrock 1.2.0\n\n"
        "မိမိလိုချင်တဲ့ File​ အမည်ကို Copy ယူပါ။"
    )
    await update.message.reply_text(file_list)

# /tutorial command
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide_text = (
        "Bot အသုံးပြုနည်း Tutorial\n\n"
        "• /list ထဲက မိမိလိုချင်တဲ့​ File​ အမည်ကို Copy ယူပါ။\n"
        "• ၎င်းအမည်ကို Bot ထံ စာရိုက်ပို့လိုက်ပါ။\n"
        "• Bot မှ သက်ဆိုင်ရာ File ကို အလိုအလျောက် ပို့ပေးပါလိမ့်မယ်။\n\n"
        "Help Center: @amcrafter_bot"
    )
    await update.message.reply_text(guide_text)

# စာရိုက်ပို့လျှင် File ပြန်ပို့ပေးမည့်စနစ်
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return

    text = update.message.text.strip()
    
    # --- File Database (ဒီနေရာမှာ သင့် File ID တွေ ထည့်ပါ) ---
    file_database = {
        "MC​ Last Version": "FILE_ID_HERE"
        "Actions and Stuff 1.10": "FILE_ID_HERE",
        "Item Physics & More": "FILE_ID_HERE",
        "MM Standard UI V1": "FILE_ID_HERE"
        "RealismCraft 2.4": "FILE_ID_HERE"
        "Naturalist 26.1": "FILE_ID_HERE"
        "RealismCraft 2.4": "FILE_ID_HERE"
        "Better on Bedrock 1.2.0": "FILE_ID_HERE"
    }

    if text in file_database:
        file_id = file_database[text]
        if file_id == "FILE_ID_HERE":
            await update.message.reply_text("ဒီ​ File​ မရှိ့သေးပါဘူးဗျ။")
        else:
            try:
                await update.message.reply_document(document=file_id)
            except Exception as e:
                await update.message.reply_text(f"Error: {str(e)}")
    else:
        await update.message.reply_text("မရှိသော​ File​ အမည် ဖြစ်နေပါတယ်။ /list ထဲကအတိုင်း တိကျစွာ ရေးပေးပါ။")

# --- 4. Main Program ---
def main():
    # Render အတွက် Web Server ကို Background မှာ အရင်ဖွင့်ထားမယ်
    keep_alive()

    # Telegram Bot ကို Setup လုပ်မယ်
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_files))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
