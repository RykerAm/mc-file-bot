import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- Settings ---
TOKEN = '8512047741:AAGpAQ6GGKS8V_8eXBQ9g7U__UYUXUZGpbw'
CHANNEL_ID = '@MinecraftMyanmarMCM'

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
        keyboard = [[InlineKeyboardButton("Join  ရန်နှိပ်ပါ", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"Channel အရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\n"
            f"(Join ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ)",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        f"Welcome ပါဗျ။\n"
        f"Bot ကိုစတင်အသုံးပြုနိုင်ပါပြီ။\n\n"
        f"ရယူနိုင်သော File များစာရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပါ။\n"
        f"Bot အသုံးပြုနည်းကြည့်ရန် /tutorial ကိုနှိပ်ပါ။"
    )


async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return
    file_list = (
        "ရယူနိုင်သော File များစာရင်း -\n\n"
        "1. Actions and Stuff 1.10\n"
        "2. Item Physics & More\n"
        "3. MM Standard UI V1\n\n"
        "File ရယူရန် အပေါ်က အမည်အတိုင်း​ တိကျစွာရိုက်ပို့ပေးပါ။"
    )
    await update.message.reply_text(file_list)

# --- Tutorial Command အသစ် ---
async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    guide_text = (
        "Advance File Bot အသုံးပြုနည်း​ Tutorial\n\n"
        "/list ကိုနှိပ်ပြီး ရယူနိုင်မယ့် File စာရင်းများကိုကြည့်ရှု့နိုင်ပါတယ်။\n"
        "File ရယူလိုပါက ကိုယ်လိုခြင်တဲ့ File ရဲ့​ Name ကိုတိကျစွာရိုက်ပို့ပေးဖို့လိုပါမယ် (List ထဲမှာပါတဲ့​ File တွေဘဲရပါမယ်)​\n"
        "Owner နဲ့​တိုက်ရိုက်​စကားပြောရန်​ -​ @amcrafter_bot\n\n"
     )
    await update.message.reply_text(guide_text, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    joined = await is_user_joined(update, context)
    if not joined:
        await start(update, context)
        return

    if update.message.document:
        file_id = update.message.document.file_id
        await update.message.reply_text(f"ဒီဖိုင်ရဲ့ ID အသစ်က -\n\n{file_id}")
        return

    if update.message.text:
        text = update.message.text.strip()
        # နောက်မှ File ID တွေ ဒီမှာ လာထည့်ပါ
        file_database = {
            "Actions and Stuff 1.10": "FILE_ID_HERE",
            "Item Physics & More": "FILE_ID_HERE",
            "MM Standard UI V1": "FILE_ID_HERE"
        }

        if text in file_database:
            if file_database[text] == "FILE_ID_HERE":
                await update.message.reply_text("ဒီဖိုင်အတွက် ID မထည့်ရသေးပါဘူး။")
            else:
                try:
                    await update.message.reply_document(document=file_database[text])
                except Exception:
                    await update.message.reply_text("Error: ID မှားနေပါတယ်။")
        elif not text.startswith('/'):
            await update.message.reply_text("File ရှာမတွေ့ပါ။ စာလုံးပေါင်း ပြန်စစ်ပေးပါ။")

def main():
    app = Application.builder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("list", list_files))
    app.add_handler(CommandHandler("tutorial", tutorial)) # Tutorial handler ထည့်သွင်းခြင်း
    app.add_handler(MessageHandler(filters.TEXT | filters.Document.ALL, handle_message))
    
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__': # ပြင်ဆင်ထားသော main check
    main()
