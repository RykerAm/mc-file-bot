import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (Render Port Error ကျော်ရန်) ---
app = Flask('')
@app.route('/')
def home(): return "Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    Thread(target=run).start()

# --- 2. Bot Settings ---
TOKEN = '8512047741:AAGpAQ6GGKS8V_8eXBQ9g7U__UYUXUZGpbw'
CHANNEL_ID = '@MinecraftMyanmarMCM'

# --- 3. Bot Logic ---

# Join မ Join စစ်ခြင်း
async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

# /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        keyboard = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
        await update.message.reply_text("⚠️ Bot ကိုအသုံးပြုရန် Channel အရင် Join ပေးပါဗျ။", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    await update.message.reply_text("👋 Welcome! Minecraft Myanmar File Bot မှ ကြိုဆိုပါတယ်။\n\n📜 ဖိုင်စာရင်းကြည့်ရန် - /list\n📖 အသုံးပြုနည်းကြည့်ရန် - /tutorial")

# /list Command
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined: return await start(update, context)
    
    file_list = (
        "📜 **ရရှိနိုင်သော File များစာရင်း**\n\n"
        "1. `Actions and Stuff 1.10` \n"
        "2. `Item Physics & More` \n"
        "3. `MM Standard UI V1` \n\n"
        "💡 ဖိုင်အမည်ကို ဖိပြီး Copy ကူးပြီး Bot ဆီ ပြန်ပို့ပေးပါ။"
    )
    await update.message.reply_text(file_list, parse_mode='Markdown')

# /tutorial Command (User အတွက်)
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide = (
        "📖 **Bot အသုံးပြုနည်းလမ်းညွှန်**\n\n"
        "1️⃣ အရင်ဆုံးပေးထားတဲ့ Channel ကို Join ပါ။\n"
        "2️⃣ /list ကိုနှိပ်ပြီး မိမိလိုချင်တဲ့ ဖိုင်အမည်ကို ကြည့်ပါ။\n"
        "3️⃣ ဖိုင်အမည်ကို Copy ယူပြီး Bot ထံ စာရိုက်ပို့ပါ။\n"
        "4️⃣ Bot မှ ဖိုင်ကို ခဏအတွင်း ပို့ပေးပါလိမ့်မည်။\n\n"
        "⚠️ **သတိပြုရန်** - စာလုံးပေါင်း တိကျစွာ ရိုက်ပို့ပေးရပါမည်။"
    )
    await update.message.reply_text(guide, parse_mode='Markdown')

# File ID ထုတ်ပေးခြင်း (Admin အတွက် Tutorial ပါဝင်သည်)
async def get_file_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    file = None
    if update.message.document: file = update.message.document
    elif update.message.video: file = update.message.video
    elif update.message.photo: file = update.message.photo[-1]

    if file:
        response = (
            "✅ **File ID ရရှိပါပြီ!**\n\n"
            f"`{file.file_id}`\n\n"
            "🛠 **Admin Tutorial:**\n"
            "ဒီ ID ကို Copy ကူးပြီး GitHub ရှိ `file_database` ထဲက သက်ဆိုင်ရာဖိုင်အမည်ဘေးမှာ ထည့်ပေးလိုက်ပါ။"
        )
        await update.message.reply_text(response, parse_mode='Markdown')

# User စာရိုက်ပို့လျှင် ဖိုင်ပြန်ပို့ပေးခြင်း
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined: return

    text = update.message.text.strip()
    
    # --- File Database (ဒီနေရာမှာ ID တွေ အစားထိုးပါ) ---
    file_database = {
        "Actions and Stuff 1.10": "ဒီနေရာမှာ_ID_ထည့်ပါ",
        "Item Physics & More": "ဒီနေရာမှာ_ID_ထည့်ပါ",
        "MM Standard UI V1": "ဒီနေရာမှာ_ID_ထည့်ပါ"
    }

    if text in file_database:
        fid = file_database[text]
        if fid == "ဒီနေရာမှာ_ID_ထည့်ပါ":
            await update.message.reply_text("❌ ဒီဖိုင်အတွက် ID မထည့်ရသေးပါဘူး။ (Admin ကို အကြောင်းကြားပါ)")
        else:
            await update.message.reply_document(document=fid)
    else:
        await update.message.reply_text("❓ မရှိသောဖိုင်အမည်ပါ။ /list ကိုပြန်စစ်ပါ။")

def main():
    keep_alive()
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("tutorial", tutorial))
    
    # File ပို့ရင် ID ထုတ်ပေးဖို့
    app.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO | filters.PHOTO, get_file_id))
    # စာရိုက်ရင် ဖိုင်ရှာပေးဖို့
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    
    app.run_polling()

if __name__ == '__main__':
    main()
