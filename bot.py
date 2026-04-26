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
            "Channel အရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ\n\nJoin ပြီးပါက /start ကို ပြန်နှိပ်ပါ။",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        "Welcome ပါဗျ Advance File Bot ကိုစတင်အသုံးပြုနိုင်ပါပြီ။\n\nရယူနိုင်သော File များစာရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပါ\nAdvance File Bot အသုံးပြုနည်းကြည့်ရန် /tutorial ကိုနှိပ်ပါ"
    )

# /list command
async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return
    
    file_list = (
        "ရယူနိုင်သော File များစာရင်း -\n\n"
        "• MC Latest Version\n"
        "• Actions and Stuff 1.10\n"
        "• Item Physics and More\n"
        "• MM Standard UI V1\n"
        "• RealismCraft 2.4\n"
        "• Naturalist 26.1\n"
        "• RLCraft Bedrock Edition 1.2\n"
        "• Better on Bedrock 1.2.0\n\n"
        "မိမိလိုချင်တဲ့ File အမည်ကို Copy ယူပြီး Bot ထံ စာရိုက်ပို့ပါ။"
    )
    await update.message.reply_text(file_list)

# /tutorial command
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide_text = (
        "Bot အသုံးပြုနည်း Tutorial\n\n"
        "• /list ထဲက မိမိလိုချင်တဲ့ File အမည်ကို Copy ယူပါ။\n"
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
    
    # --- File Database (IDs များ ဖြည့်သွင်းပြီး) ---
    file_database = {
        "MC Latest Version": "BQACAgUAAxkBAAPSae3GrY1WuUPHvKs2AeS1RsuEF10AAjUgAALsw7BWgGJ6b9XdgE47BA",
        "Actions and Stuff 1.10": "BQACAgUAAxkBAAN8ae2Pno_5SA2Xl5oFYn77DdM3JkIAAmsfAAKy0QFXhA1GvRBwzoc7BA",
        "Item Physics and More": "BQACAgIAAxkBAAO7ae2z_8HqmEzTBjdyiNPKp9-BI70AAkqgAALlivlKnVlstDtu9UI7BA",
        "MM Standard UI V1": "BQACAgUAAxkBAAPYae3G6SGZjaLCNg3Cw4Rj7Uwwm28AAhMbAAL9UqBWyz_ru8tLC2s7BA",
        "RealismCraft 2.4": "BQACAgIAAxkBAAPaae3G9kB6rirexo0X2SXyQGCa7ZMAAnSfAAJx6wABS2Tv1hYxi5zIOwQ",
        "Naturalist 26.1": "BQACAgIAAxkBAAPcae3HAbvq5mOvstoVbUEx7ea1nGoAAq-ZAAKJ0WBK_HhGojbxuM47BA",
        "RLCraft Bedrock Edition 1.2": "BQACAgUAAxkBAAPeae3HCxzsNky4UxYfy7flJoNft5IAAqscAAIWHWBX-7mP3C3_sHw7BA",
        "Better on Bedrock 1.2.0": "BQACAgUAAxkBAAPgae3HF3HwsyhvlPn9fPxi6Bh18CwAArcaAAKtWilWQFXbeAwkmgc7BA"
    }

    if text in file_database:
        file_id = file_database[text]
        try:
            await update.message.reply_document(document=file_id, caption=f"ဒီမှာပါ {text} File ဖြစ်ပါတယ်ဗျ။")
        except Exception as e:
            await update.message.reply_text(f"Error: File ပို့ရာတွင် အဆင်မပြေဖြစ်နေပါသည်။ ({str(e)})")
    else:
        # File ရှာမတွေ့ရင် /list ပြန်ပြခိုင်းတာ ပိုကောင်းပါတယ်
        await update.message.reply_text("မရှိသော File အမည် ဖြစ်နေပါတယ်။ /list ထဲကအတိုင်း စာလုံးပေါင်း တိကျစွာ ရေးပေးပါ။")

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
