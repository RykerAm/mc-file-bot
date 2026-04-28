import logging
import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online and Running!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. Bot Settings ---
TOKEN = '8512047741:AAGpAQ6GGKS8V_8eXBQ9g7U__UYUXUZGpbw'
CHANNEL_ID = '@MinecraftMyanmarMCM'
ADMIN_ID = 6112249043

user_list = set()
group_list = set()

# --- 3. Bot Logic ---

async def is_user_joined(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception:
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.effective_chat.type == 'private':
        user_list.add(user_id)
    
    joined = await is_user_joined(update, context)
    if not joined:
        keyboard = [[InlineKeyboardButton("Join ရန်နှိပ်ပါ", url=f"https://t.me/{CHANNEL_ID.replace('@', '')}")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "ကျနော်ရဲ့ MCM Channel ကို အရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ\n\nJoin ပြီးပါက /start ကို ပြန်နှိပ်ပေးပါ။",
            reply_markup=reply_markup
        )
        return

    await update.message.reply_text(
        "Welcome ပါဗျာ Advance File Bot ကိုစတင်အသုံးပြုနိုင်ပါပြီ။\n\nရယူနိုင်သော File များစာရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပါ\nအသုံးပြုနည်းကြည့်ရန် /tutorial ကိုနှိပ်ပါ"
    )

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await is_user_joined(update, context):
        await start(update, context)
        return
    
    file_list = (
        "ရယူနိုင်သော File များစာရင်း -\n\n"
        "• MC Latest Version\n"
        "• Actions and Stuff 1.10\n"
        "• Item Physics and More\n"
        "• One Piece\n"
        "• RealismCraft 2.4\n"
        "• Naturalist 26.1\n"
        "• RLCraft Bedrock Edition 1.2\n"
        "• Better on Bedrock 1.2.0\n"
        "• Essential 1.8.0\n"
        "• Java Combat\n"
        "• Bare Bones\n"
        "• Effortless Building V2.0\n"
        "• Better on Bedrock Map\n"
        "• More Structures\n"
        "• Death Animations v1.2\n"
        "• Realistic Seasons\n"
        "• One Piece Asa v68.0.0\n"
        "• Furniture 2.1\n"
        "• Dynamic First Person Model\n"
        "• Actual Guns 2\n"
        "• Core Craft v1.1.5\n"
        "• One Block (Like Java)\n"
        "• Demon Slayer Addon v11\n"
        "• Attack on Titan\n"
        "• Prizma Visuals\n\n"
        "မိမိလိုချင်တဲ့ File အမည်ကို Copy ယူပြီး Bot ထံ စာရိုက်ပို့ပါ။"
    )
    await update.message.reply_text(file_list)

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Bot အသုံးပြုနည်း Tutorial\n\n"
        "1. /list ထဲမှ မိမိလိုချင်သော File အမည်ကို Copy ယူပါ။\n"
        "2. ၎င်းအမည်ကို Bot ထံ စာရိုက်ပို့လိုက်ပါ။\n"
        "3. Bot မှ သက်ဆိုင်ရာ File ကို အလိုအလျောက် ပို့ပေးပါလိမ့်မည်။\n\n"
        "Help Center: @amcrafter_bot"
    )

# --- 4. Admin Only Broadcast (Copy Message) ---

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Formatting မပျက်စေရန် ပို့ချင်တဲ့စာကို Reply ပြန်ပြီး /broadcast ရိုက်ပါ။")
        return
    
    count = 0
    target_msg = update.message.reply_to_message
    for uid in list(user_list):
        try:
            await context.bot.copy_message(chat_id=uid, from_chat_id=update.message.chat_id, message_id=target_msg.message_id)
            count += 1
        except Exception: continue
    await update.message.reply_text(f"✅ User {count} ယောက်ထံ Formatting အပြည့်ဖြင့် ပို့ပြီးပါပြီ။")

async def gbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID: return
    if not update.message.reply_to_message:
        await update.message.reply_text("❌ Formatting မပျက်စေရန် ပို့ချင်တဲ့စာကို Reply ပြန်ပြီး /gbroadcast ရိုက်ပါ။")
        return
    
    if not group_list:
        await update.message.reply_text("⚠️ Memory ထဲတွင် Group မရှိသေးပါ။ Group ထဲတွင် စာအရင်သွားရိုက်ပါ။")
        return

    count = 0
    target_msg = update.message.reply_to_message
    for gid in list(group_list):
        try:
            await context.bot.copy_message(chat_id=gid, from_chat_id=update.message.chat_id, message_id=target_msg.message_id)
            count += 1
        except Exception: continue
    await update.message.reply_text(f"✅ Group {count} ခုသို့ Formatting အပြည့်ဖြင့် ပို့ပြီးပါပြီ။")

# --- 5. Message Handling ---

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user_id = update.effective_user.id

    if chat.type in ['group', 'supergroup']:
        group_list.add(chat.id)
        return 
    else:
        user_list.add(user_id)

    # Admin Only: File to ID
    if update.message.document:
        if user_id == ADMIN_ID:
            f_id = update.message.document.file_id
            await update.message.reply_text(f"File ID ရရှိပါပြီ\n\nID: `{f_id}`", parse_mode='Markdown')
        return

    text = update.message.text.strip() if update.message.text else ""
    
    file_database = {
        "MC Latest Version": "BQACAgUAAxkBAAPSae3GrY1WuUPHvKs2AeS1RsuEF10AAjUgAALsw7BWgGJ6b9XdgE47BA",
        "Actions and Stuff 1.10": "BQACAgUAAxkBAAN8ae2Pno_5SA2Xl5oFYn77DdM3JkIAAmsfAAKy0QFXhA1GvRBwzoc7BA",
        "Item Physics and More": "BQACAgIAAxkBAAO7ae2z_8HqmEzTBjdyiNPKp9-BI70AAkqgAALlivlKnVlstDtu9UI7BA",
        "One Piece": "BQACAgUAAxkBAAMpafBb6kAUhe1BU-c42QegfAglgRIAAhobAAKW-6hVc0seKc38Ncg7BA",
        "RealismCraft 2.4": "BQACAgIAAxkBAAPaae3G9kB6rirexo0X2SXyQGCa7ZMAAnSfAAJx6wABS2Tv1hYxi5zIOwQ",
        "Naturalist 26.1": "BQACAgIAAxkBAAPcae3HAbvq5mOvstoVbUEx7ea1nGoAAq-ZAAKJ0WBK_HhGojbxuM47BA",
        "RLCraft Bedrock Edition 1.2": "BQACAgUAAxkBAAPeae3HCxzsNky4UxYfy7flJoNft5IAAqscAAIWHWBX-7mP3C3_sHw7BA",
        "Better on Bedrock 1.2.0": "BQACAgUAAxkBAAPgae3HF3HwsyhvlPn9fPxi6Bh18CwAArcaAAKtWilWQFXbeAwkmgc7BA",
        "Essential 1.8.0": "BQACAgUAAxkBAAIDEmnwOUkcP7mtbfvaN5ztNTIqMi1OAAJ-IAACNo-BV8rNvm41y8F4OwQ",
        "Java Combat": "BQACAgUAAxkBAAIDTWnwReA1ZDRHLEj5Qsa89sR6yytkAAK2GAACTDKJVuia9cxr7mp5OwQ",
        "Bare Bones": "BQACAgQAAxkBAAIDWWnwSk6_Zta3uziNOzNaa43u8aJoAALxGQACRBSBUx2RoVSftGaSOwQ",
        "Effortless Building V2.0": "BQACAgUAAxkBAAIDW2nwSp-FScPqEmdZesBIzXzsv0qUAALXIQACsQ44V4sakXAdfGfaOwQ",
        "Better on Bedrock Map": "BQACAgIAAxkBAAIDXWnwStfCzh9QGkfpfT89N4L0Yr84AAIkmwACXudISwWdNT8Cd5slOwQ",
        "More Structures": "BQACAgIAAxkBAAICAmnvE2e2a8v2IrryLkMs3n4yIIw6AAOWAAIERBhKeUUslp6gsDI7BA",
        "Death Animations v1.2": "BQACAgIAAxkBAAIDY2nwSwqI4pJuhhV5nuEjqFpRwagCAALykQACWF_YSJ0CPlkavUsUOwQ",
        "Realistic Seasons": "BQACAgIAAxkBAAIDZWnwSxB6otYZmgJd_J9hY2GUb43cAALAnQACEDFgStecJU9iFO-rOwQ",
        "One Piece Asa v68.0.0": "BQACAgUAAxkBAAIDZ2nwSzXMlufNUUKh-08WxU0_ubGvAAIaGwAClvuoVdDfJAEsodbiOwQ",
        "Furniture 2.1": "BQACAgIAAxkBAAIDpWnwv_EFkvCf9zY8iELHEMTD6wABDAAC7KEAAl4ISUr3IfayUW93CTsE",
        "Dynamic First Person Model": "BQACAgIAAxkBAAIDp2nwv_g9WCOHnCAWpzzjC6Ik1aqPAAKNlQAC9wPpSkuJKWPMY-0XOwQ",
        "Actual Guns 2": "BQACAgUAAxkBAAIDqWnwv_-7DqzhuSRc_DA9oVx-jbgqAAIfHQACAjkxV7Jc9bLZVCrNOwQ",
        "Core Craft v1.1.5": "BQACAgUAAxkBAAIDq2nwwAekUoFgn2wZ0whFEQPt6QnUAAIgGwAC_gs5V8F7BC9I9yJWOwQ",
        "One Block (Like Java)": "BQACAgUAAxkBAAIDrWnwwA6XggoU6BKy4eh8Mdvc-j1qAAIMFQACJRAZVLD14wmE1V1bOwQ",
        "Demon Slayer Addon v11": "BQACAgUAAxkBAAIDr2nwwBfmTtE_pMbZW6J3Y5VhtZTEAAJpFwACpThBVUoG6E4b_b-bOwQ",
        "Attack on Titan": "BQACAgIAAxkBAAIDsWnwwCqaRkJJHIBv_X4j7MxN0kNzAAK0egACqoMISkOU9FRYQlAGOwQ",
        "Prizma Visuals": "BQACAgIAAxkBAAIDs2nwwDIOYjjNx-mwxMHjcwomriHJAALPigACENcISNwySijdw2CoOwQ"
    }

    if text in file_database:
        if not await is_user_joined(update, context):
            await start(update, context)
            return
        try:
            await update.message.reply_document(document=file_database[text], caption=f"{text} File ပါ။")
        except Exception:
            await update.message.reply_text("Error: File ပို့ရာတွင် အခက်အခဲရှိနေပါသည်။")
    elif text and chat.type == 'private' and not text.startswith('/'):
        await update.message.reply_text("မရှိသော File အမည်ပါ။ စာလုံးပေါင်းမှားနေပါသလား သို့မဟုတ် /list ကို ပြန်စစ်ပေးပါ။")

def main():
    keep_alive()
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("list", list_files))
    application.add_handler(CommandHandler("tutorial", tutorial))
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("gbroadcast", gbroadcast))
    
    application.add_handler(MessageHandler(filters.ALL, handle_message))

    print("Bot is starting...")
    application.run_polling()

if __name__ == '__main__':
    main()
