import os
import asyncio
import random
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 1. Flask Web Server (Render အတွက်) ---
app = Flask('')

@app.route('/')
def home():
    return "Bot is Online and Running Smoothly!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. Bot Settings ---
TOKEN = '8512047741:AAFGZ0dCg8MQ6hoUUBja-6dCchdgHkoIc70'
OWNER_ID = 6112249043 
CHANNEL_ID = '@MinecraftMyanmarMCM'

# --- 3. Database (ဖိုင် ၄၃ ခုလုံး အပြည့်အစုံ) ---
file_database = {
    "Addons": {
        "Actions and Stuff 1.10": "BQACAgUAAxkBAAN8ae2Pno_5SA2Xl5oFYn77DdM3JkIAAmsfAAKy0QFXhA1GvRBwzoc7BA",
        "One Piece": "BQACAgUAAxkBAAMpafBb6kAUhe1BU-c42QegfAglgRIAAhobAAKW-6hVc0seKc38Ncg7BA",
        "Essential 1.8.0": "BQACAgUAAxkBAAIDEmnwOUkcP7mtbfvaN5ztNTIqMi1OAAJ-IAACNo-BV8rNvm41y8F4OwQ",
        "Java Combat": "BQACAgUAAxkBAAIDTWnwReA1ZDRHLEj5Qsa89sR6yytkAAK2GAACTDKJVuia9cxr7mp5OwQ",
        "Naturalist 26.1": "BQACAgIAAxkBAAPcae3HAbvq5mOvstoVbUEx7ea1nGoAAq-ZAAKJ0WBK_HhGojbxuM47BA",
        "Effortless Building V2.0": "BQACAgUAAxkBAAIDW2nwSp-FScPqEmdZesBIzXzsv0qUAALXIQACsQ44V4sakXAdfGfaOwQ",
        "More Structures": "BQACAgIAAxkBAAICAmnvE2e2a8v2IrryLkMs3n4yIIw6AAOWAAIERBhKeUUslp6gsDI7BA",
        "Death Animations v1.2": "BQACAgIAAxkBAAIDY2nwSwqI4pJuhhV5nuEjqFpRwagCAALykQACWF_YSJ0CPlkavUsUOwQ",
        "Realistic Seasons": "BQACAgIAAxkBAAIDZWnwSxB6otYZmgJd_J9hY2GUb43cAALAnQACEDFgStecJU9iFO-rOwQ",
        "One Piece Asa v68.0.0": "BQACAgUAAxkBAAIDZ2nwSzXMlufNUUKh-08WxU0_ubGvAAIaGwAClvuoVdDfJAEsodbiOwQ",
        "Furniture v2.1": "BQACAgIAAxkBAAIDpWnwv_EFkvCf9zY8iELHEMTD6wABDAAC7KEAAl4ISUr3IfayUW93CTsE",
        "Dynamic First Person Model": "BQACAgIAAxkBAAIDp2nwv_g9WCOHnCAWpzzjC6Ik1aqPAAKNlQAC9wPpSkuJKWPMY-0XOwQ",
        "Actual Guns 2": "BQACAgUAAxkBAAIDqWnwv_-7DqzhuSRc_DA9oVx-jbgqAAIfHQACAjkxV7Jc9bLZVCrNOwQ",
        "Core Craft v1.1.5": "BQACAgUAAxkBAAIDq2nwwAekUoFgn2wZ0whFEQPt6QnUAAIgGwAC_gs5V8F7BC9I9yJWOwQ",
        "Demon Slayer Addon v11": "BQACAgUAAxkBAAIDr2nwwBfmTtE_pMbZW6J3Y5VhtZTEAAJpFwACpThBVUoG6E4b_b-bOwQ",
        "Attack on Titan": "BQACAgIAAxkBAAIDsWnwwCqaRkJJHIBv_X4j7MxN0kNzAAK0egACqoMISkOU9FRYQlAGOwQ",
        "Overhauled Farming Food": "BQACAgUAAxkBAAISWGn0vHtfrrED6HOMqcR5tuOGgDJlAALqHgACjfppV5yeyu1wiGuwOwQ",
        "Travelcraft Add-On": "BQACAgUAAxkBAAISWmn0vIh0DSbaHM95tUhhAU7tVAhlAAKmIwAC3quRV_WzUSesAWN2OwQ",
        "Vein Capitator v2.4.2": "BQACAgUAAxkBAAISXmn0vLPHmqo7jrAn5rCU4oNJ9Vg0AAJLIgACi4uQVEgmGt-4MW2hOwQ",
        "Playmate": "BQACAgUAAxkBAAISYGn0vNWVX5hAXh5BpWbDOfZLdxJ-AAKvGwACMiPwVkBCPO_8LzkcOwQ",
        "Naruto Craft": "BQACAgUAAxkBAAISYmn0vOE8LThhiNOl2Uo8aUVS7qzdAAIvJgACPGbYViQm1aDSJaLDOwQ",
        "Biomes+": "BQACAgUAAxkBAAISZGn0vOu9AuAchlL54yLb3EtRvPx1AAIqGgACe9DJVjZmyhgtuLUQOwQ"
    },
    "Texture Pack": {
        "Bare Bones": "BQACAgQAAxkBAAIDWWnwSk6_Zta3uziNOzNaa43u8aJoAALxGQACRBSBUx2RoVSftGaSOwQ",
        "MM Standard UI V1": "BQACAgUAAxkBAAPYae3G6SGZjaLCNg3Cw4Rj7Uwwm28AAhMbAAL9UqBWyz_ru8tLC2s7BA",
        "Slot Hotbar Button v1.2.1": "BQACAgUAAxkBAAISXGn0vKEIr2BJP1c4p8SIKyneYpY1AAJaGwACGmtYV4BIepsSAAE2DzsE",
        "No Damage": "BQACAgIAAxkBAAISZmn0vRb-wfjtFxZT68O9ig_QMtUMAAIdFgACzY6xVo21eOTACturOwQ",
        "Keep Inventory": "BQACAgIAAxkBAAISaGn0vR7CujJswXZ6XLATeQwDkVbvAALrEwAC9hexVv4yjfCwZ0aPOwQ",
        "No Creeper Explosion": "BQACAgIAAxkBAAISamn0vSQm-M7-xNrsBVFsJwZiaChcAAJmFAAC9hexVrhFoyF4KEl-OwQ",
        "La Nature Alpla": "BQACAgUAAxkBAAISfWn0v8zh9dEMxLvujz52xdfuo1YRAAK_HQACOuOxVuaCSeT2qo6BOwQ"
    },
    "Shader Pack": {
        "Prizma Visuals": "BQACAgIAAxkBAAIDs2nwwDIOYjjNx-mwxMHjcwomriHJAALPigACENcISNwySijdw2CoOwQ",
        "Newb X RTX": "BQACAgUAAxkBAAISf2n0v-NusHvOXFZg1wLZkYJQgr_7AAIzGQACYesJVhO3G6qL3bFmOwQ",
        "Dark Fantasy Visuals": "BQACAgUAAxkBAAISgmn0v_b8FgthZQmJUTzWn11voTyZAAIrGgACfAjZVH3-ITabo-2cOwQ",
        "Solar Shader V7": "BQACAgUAAxkBAAIShWn0wAlVdLpv2xzajWzHDLS7eksFAALXFgAC6F_5Ve9SvOqDocePOwQ"
    },
    "World/Map": {
        "RealismCraft 2.4": "BQACAgIAAxkBAAPaae3G9kB6rirexo0X2SXyQGCa7ZMAAnSfAAJx6wABS2Tv1hYxi5zIOwQ",
        "RLCraft Bedrock Edition": "BQACAgUAAxkBAAPeae3HCxzsNky4UxYfy7flJoNft5IAAqscAAIWHWBX-7mP3C3_sHw7BA",
        "Better on Bedrock V1.2.0": "BQACAgUAAxkBAAPgae3HF3HwsyhvlPn9fPxi6Bh18CwAArcaAAKtWilWQFXbeAwkmgc7BA",
        "One Block (Like Java)": "BQACAgUAAxkBAAIDrWnwwA6XggoU6BKy4eh8Mdvc-j1qAAIMFQACJRAZVLD14wmE1V1bOwQ"
    },
    "MC Version": {
        "MC 1.21.0 (Latest)": "BQACAgUAAxkBAAPSae3GrY1WuUPHvKs2AeS1RsuEF10AAjUgAALsw7BWgGJ6b9XdgE47BA"
    }
}

# --- 4. Logic Functions ---

async def is_user_joined(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ['member', 'administrator', 'creator']
    except: return False

async def show_menu(update_or_query, context: ContextTypes.DEFAULT_TYPE, edit=False):
    user = update_or_query.effective_user if hasattr(update_or_query, 'effective_user') else update_or_query.from_user
    user_id = user.id
    
    if not await is_user_joined(user_id, context):
        text = "ကျနော်ရဲ့ MCM Channel ကိုအရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\nJoin ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ"
        kb = [[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID.replace('@','')}")]]
        if edit:
            try: await update_or_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(kb))
            except: pass
        else:
            await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
        return

    keyboard = [
        [InlineKeyboardButton("Addons", callback_data="cat_Addons"), InlineKeyboardButton("Texture Pack", callback_data="cat_Texture Pack")],
        [InlineKeyboardButton("Shader Pack", callback_data="cat_Shader Pack"), InlineKeyboardButton("World/Map", callback_data="cat_World/Map")],
        [InlineKeyboardButton("MC Version", callback_data="cat_MC Version")],
        [InlineKeyboardButton("🎲 Random File", callback_data="random_file")]
    ]
    text = "<b>File Type များ</b>\n\nအောက်ပါ Category များထဲမှ သင်နှစ်သက်ရာကို ရွေးချယ်နိုင်ပါသည်။"
    
    if edit:
        try: await update_or_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')
        except: pass
    else:
        await update_or_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='HTML')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>Welcome ပါဗျာ</b>\n\n<b>Advance File Bot 4.0</b>\n\n/list ကိုနှိပ်ပြီး စတင်အသုံးပြုနိုင်ပါပြီ။", parse_mode='HTML')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    user_id = update.effective_user.id
    
    text = update.message.text.strip()
    if text.startswith('/'): return
    if not await is_user_joined(user_id, context): return

    found = []
    for cat in file_database.values():
        for name, fid in cat.items():
            if text.lower() in name.lower(): found.append((name, fid))
    
    if not found:
        await update.message.reply_text("File ရှာမတွေ့ပါ။ နာမည်မှန်အောင်ပြန်ရိုက်ပေးပါ။")
    elif len(found) == 1:
        # User အားနာစရာမလိုအောင် Sleep ဖြုတ်ထားပါတယ်၊ ပိုမြန်သွားပါမယ်
        await update.message.reply_document(document=found[0][1], caption=f"ဒီမှာပါ <b>{found[0][0]}</b>", parse_mode='HTML')
    else:
        res = "ရှာတွေ့သည့် File များ:\n"
        for f in found: res += f"• <code>{f[0]}</code>\n"
        await update.message.reply_text(res, parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "main_list":
        await show_menu(query, context, edit=True)
    elif query.data == "random_file":
        all_f = [(n, f) for c in file_database.values() for n, f in c.items()]
        name, fid = random.choice(all_f)
        await query.message.reply_document(document=fid, caption=f"Random: <b>{name}</b>", parse_mode='HTML')
    elif query.data.startswith("cat_"):
        cat_name = query.data.replace("cat_", "")
        files = file_database.get(cat_name, {})
        res = f"<b>{cat_name}</b>\n\n"
        for f in files.keys(): res += f"• <code>{f}</code>\n"
        kb = [[InlineKeyboardButton("⬅️ Back", callback_data="main_list")]]
        await query.edit_message_text(res, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

def main():
    keep_alive()
    # Connection ပိုငြိမ်အောင် timeout ညှိထားပါတယ်
    app_bot = Application.builder().token(TOKEN).read_timeout(20).write_timeout(20).build()
    
    app_bot.add_handler(CommandHandler("start", start))
    app_bot.add_handler(CommandHandler("list", lambda u, c: show_menu(u, c, edit=False)))
    app_bot.add_handler(CallbackQueryHandler(button_handler))
    app_bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Message အဟောင်းတွေကို ကျော်လိုက်ပြီး လက်ရှိ message တွေကိုပဲ အမြန်ပြန်ဖြေပါမယ်
    app_bot.run_polling(drop_pending_updates=True)

if __name__ == '__main__': main()
