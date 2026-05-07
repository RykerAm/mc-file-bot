import os
import pg8000.native
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 1. Flask Web Server (For 24/7 Hosting) ---
app = Flask('')
@app.route('/')
def home(): return "Advance File V6.3 bot is Online!"
def run(): app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 8080)))
def keep_alive():
    t = Thread(target=run); t.daemon = True; t.start()

# --- 2. Configuration & Database ---
TOKEN = '8512047741:AAFGZ0dCg8MQ6hoUUBja-6dCchdgHkoIc70'
OWNER_ID = 6112249043 
CHANNEL_ID = '@MinecraftMyanmarMCM'

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
        "26.13": "BQACAgUAAxkBAAPSae3GrY1WuUPHvKs2AeS1RsuEF10AAjUgAALsw7BWgGJ6b9XdgE47BA"
    }
}

def get_db():
    return pg8000.native.Connection(user="postgres", password="T74KeLnyE_%jkGv", host="db.orxgpwzxdiyfinzqgkaa.supabase.co", port=5432, database="postgres")

def init_db():
    c = get_db()
    c.run('CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, name TEXT, username TEXT)')
    c.run('CREATE TABLE IF NOT EXISTS groups (group_id BIGINT PRIMARY KEY)')
    c.run('CREATE TABLE IF NOT EXISTS blacklist (user_id BIGINT PRIMARY KEY)')
    c.run('CREATE TABLE IF NOT EXISTS new_files (id SERIAL PRIMARY KEY, category TEXT, file_name TEXT, file_id TEXT)')
    c.close()

# --- 3. Middlewares & Checks ---
async def check_auth(u_id, context):
    c = get_db(); ban = c.run("SELECT 1 FROM blacklist WHERE user_id = :u", u=u_id); c.close()
    if ban: return False
    try:
        m = await context.bot.get_chat_member(CHANNEL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

# --- 4. User Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    c = get_db(); c.run("INSERT INTO users VALUES (:u, :n, :un) ON CONFLICT (user_id) DO UPDATE SET name=:n, username=:un", u=u.id, n=u.first_name, un=f"@{u.username}"); c.close()
    if not await check_auth(u.id, context):
        await update.message.reply_text("ကျနော်ရဲ့ MCM Channel ကိုအရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\nJoin ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")]]))
        return
    await update.message.reply_text("<b>Welcome ပါဗျာ</b>\n\n<b>Advance File Bot 4.0 ကိုစတင်အသုံးပြုနိုင်ပါပြီ</b>\n\nရယူနိုင်သော File များစရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပေးပါ။\n\nBot အသုံးပြုနည်းကြည့်ရရန် /tutorial ကိုနှိပ်ပေးပါ။", parse_mode='HTML')

async def list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [[InlineKeyboardButton("📦 Addons", callback_data="cat_Addons"), InlineKeyboardButton("🎨 Texture Pack", callback_data="cat_Texture Pack")],[InlineKeyboardButton("✨ Shader Pack", callback_data="cat_Shader Pack"), InlineKeyboardButton("🗺️ World/Map", callback_data="cat_World/Map")],[InlineKeyboardButton("🎮 MC Version", callback_data="cat_MC Version")]]
    msg = "<b>📂 ဖိုင်အမျိုးအစားများကို ရွေးချယ်ပါ</b>"
    if update.callback_query: await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else: await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("<b>Tutorial</b>\n\n၁။ /list ထဲမှာရှိ့တဲ့ကိုယ်လိုခြင်တဲ့ Addon Name တစ်ခုကို Copy လိုက်ပါ\n၂။ Copy လုပ်ထားတဲ့ Addon Name ကိုပို့လိုက်ပါ။\n၃။ Bot က Name နဲ့သက်ဆိုင်ရာ File ကိုပြန်ပို့ပေးပါလိမ့်မယ်\n\nGroup ထဲတွင်သုံးပါက <code>/give [ဖိုင်နာမည်]</code> ဟု ရိုက်ပေးပါ။\n\n/req Owner ဆီကဖိုင်းတောင်းဆိုတာ /fb က Feedback ပို့တာ", parse_mode='HTML')

async def fb_req(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    cmd = update.message.text.split()[0][1:]
    txt = " ".join(context.args)
    if not txt:
        await update.message.reply_text(f"/{cmd} [စာသား] ဟု ရိုက်ပေးပါ။")
        return
    header = "📩 FEEDBACK" if cmd == "fb" else "🆕 REQUEST"
    admin_msg = (f"<b>{header}</b>\n━━━━━━━━━━━━━━━\n👤 <b>Name:</b> {u.first_name}\n🆔 <b>ID:</b> <code>{u.id}</code>\n🔗 <b>User:</b> @{u.username}\n📝 <b>Text:</b> {txt}\n━━━━━━━━━━━━━━━")
    await context.bot.send_message(OWNER_ID, admin_msg, parse_mode='HTML')
    await update.message.reply_text("✅ Owner ဆီသို့ပို့ပြီးပါပြီ။")

# --- 5. Admin Commands (Owner Only) ---
async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.document:
        await update.message.reply_text("❌ ဖိုင်နှင့်တွဲ၍ Caption တွင် <code>/add Category Name</code> ဟု ရိုက်ပို့ပါ။", parse_mode='HTML')
        return
    try:
        cat, name = context.args[0], " ".join(context.args[1:])
        c = get_db(); c.run("INSERT INTO new_files (category, file_name, file_id) VALUES (:c, :n, :f)", c=cat, n=name, f=update.message.document.file_id); c.close()
        await update.message.reply_text(f"✅ သိမ်းဆည်းပြီးပါပြီ - {name}")
    except: await update.message.reply_text("❌ ပုံစံမှားနေပါသည်။")

async def remove_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    name = " ".join(context.args)
    c = get_db(); c.run("DELETE FROM new_files WHERE file_name = :n", n=name); c.close()
    await update.message.reply_text(f"🗑️ ဖျက်ပြီးပါပြီ - {name}")

async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    q = update.callback_query
    p = int(q.data.split("_")[1]) if q and q.data.startswith("ul_") else 0
    c = get_db(); total = c.run("SELECT COUNT(*) FROM users")[0][0]
    users = c.run("SELECT name, username, user_id FROM users LIMIT 20 OFFSET :o", o=p*20); c.close()
    txt = f"👤 <b>Total Users: {total}</b>\n\n"
    for i, u in enumerate(users, p*20+1): txt += f"{i}. {u[0]} (@{u[1]}) - <code>{u[2]}</code>\n"
    btns = []
    if p > 0: btns.append(InlineKeyboardButton("⬅️ Back", callback_data=f"ul_{p-1}"))
    if (p+1)*20 < total: btns.append(InlineKeyboardButton("Next ➡️", callback_data=f"ul_{p+1}"))
    kb = InlineKeyboardMarkup([btns]) if btns else None
    if q: await q.edit_message_text(txt, reply_markup=kb, parse_mode='HTML')
    else: await update.message.reply_text(txt, reply_markup=kb, parse_mode='HTML')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    txt = update.message.text_html.split(None, 1)[1] if len(context.args) > 0 else None
    if not txt: return
    is_group = "gbroadcast" in update.message.text
    c = get_db(); targets = c.run("SELECT group_id FROM groups") if is_group else c.run("SELECT user_id FROM users"); c.close()
    count = 0
    for (tid,) in targets:
        try: await context.bot.send_message(tid, txt, parse_mode='HTML'); count += 1
        except: pass
    await update.message.reply_text(f"✅ {'Groups' if is_group else 'Users'} {count} ဦးထံ ပို့ဆောင်ပြီး။")

async def sms_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        target = context.args[0].replace("@","")
        msg = " ".join(context.args[1:])
        c = get_db()
        if target.isdigit(): uid = [[int(target)]]
        else: uid = c.run("SELECT user_id FROM users WHERE username ILIKE :u", u=f"@{target}")
        c.close()
        if uid: await context.bot.send_message(uid[0][0], f"📩 <b>Owner ဆီမှ စာပြန်လာပါသည်:</b>\n\n{msg}", parse_mode='HTML')
        await update.message.reply_text("✅ ပို့ပြီး။")
    except: await update.message.reply_text("❌ ပုံစံ - /Sms @username စာသား")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        uid = int(context.args[0])
        c = get_db(); c.run("INSERT INTO blacklist VALUES (:u) ON CONFLICT DO NOTHING", u=uid); c.close()
        await update.message.reply_text(f"🚫 User {uid} ကို Ban လိုက်ပါပြီ။")
    except: pass

# --- 6. Group & Search Handlers ---
async def give_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)
    if not name: return
    found = []
    for cat, fs in file_database.items():
        for n, fid in fs.items():
            if name.lower() in n.lower(): found.append((n, fid))
    c = get_db(); dbf = c.run("SELECT file_name, file_id FROM new_files WHERE file_name ILIKE :q", q=f"%{name}%"); c.close()
    for r in dbf: found.append((r[0], r[1]))
    if found: await update.message.reply_document(found[0][1], caption=found[0][0])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        c = get_db(); c.run("INSERT INTO groups VALUES (:g) ON CONFLICT DO NOTHING", g=update.effective_chat.id); c.close()
        return # Group ထဲတွင် စာရိုက်ပါက ဘာမှပြန်မလုပ် ( /give သာရမည် )
    
    u = update.effective_user
    if not await check_auth(u.id, context): return
    txt = update.message.text
    if txt and not txt.startswith('/'):
        found = []
        for cat, fs in file_database.items():
            for n, fid in fs.items():
                if txt.lower() in n.lower(): found.append((n, fid))
        c = get_db(); dbf = c.run("SELECT file_name, file_id FROM new_files WHERE file_name ILIKE :q", q=f"%{txt}%"); c.close()
        for r in dbf: found.append((r[0], r[1]))
        
        if len(found) == 1: await update.message.reply_document(found[0][1], caption=found[0][0])
        elif len(found) > 1:
            res = "🔍 <b>တွေ့ရှိသော ဖိုင်များ-</b>\n\n" + "\n".join([f"• <code>{f[0]}</code>" for f in found])
            await update.message.reply_text(res, parse_mode='HTML')

async def btn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data.startswith("ul_"): await user_list(update, context)
    elif q.data == "main": await list_menu(update, context)
    elif q.data.startswith("cat_"):
        cn = q.data.replace("cat_", ""); res = f"<b>📂 {cn}</b>\n\n"
        for f in file_database.get(cn, {}).keys(): res += f"• <code>{f}</code>\n"
        c = get_db(); dbf = c.run("SELECT file_name FROM new_files WHERE category = :c", c=cn); c.close()
        for r in dbf: res += f"• <code>{r[0]}</code> (Cloud)\n"
        await q.edit_message_text(res, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main")]]), parse_mode='HTML')

# --- 7. Main Runner ---
def main():
    init_db(); keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("list", list_menu))
    bot.add_handler(CommandHandler("tutorial", tutorial))
    bot.add_handler(CommandHandler("fb", fb_req))
    bot.add_handler(CommandHandler("req", fb_req))
    bot.add_handler(CommandHandler("add", add_file))
    bot.add_handler(CommandHandler("remove", remove_file))
    bot.add_handler(CommandHandler("user", user_list))
    bot.add_handler(CommandHandler("broadcast", broadcast))
    bot.add_handler(CommandHandler("gbroadcast", broadcast))
    bot.add_handler(CommandHandler("Sms", sms_user))
    bot.add_handler(CommandHandler("ban", ban_user))
    bot.add_handler(CommandHandler("give", give_cmd))
    bot.add_handler(CallbackQueryHandler(btn_callback))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.run_polling()

if __name__ == '__main__': main()
