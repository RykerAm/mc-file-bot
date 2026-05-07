import os
import psycopg2
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 1. Flask Web Server (For 24/7 Hosting) ---
app = Flask('')

@app.route('/')
def home():
    return "Advance File V6.3 bot is Online!"

def run():
    # Render environment variable port
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. Configuration & Database ---
TOKEN = '8512047741:AAFGZ0dCg8MQ6hoUUBja-6dCchdgHkoIc70'
OWNER_ID = 6112249043 
CHANNEL_ID = '@MinecraftMyanmarMCM'
DB_URL = "postgres://postgres:T74KeLnyE_%jkGv@db.orxgpwzxdiyfinzqgkaa.supabase.co:5432/postgres"

def get_db_conn():
    # Render နှင့် Supabase အတွက် sslmode ပါဝင်သော connection
    return psycopg2.connect(DB_URL, sslmode='require')

def init_db():
    conn = get_db_conn()
    cur = conn.cursor()
    cur.execute('CREATE TABLE IF NOT EXISTS users (user_id BIGINT PRIMARY KEY, name TEXT, username TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS groups (group_id BIGINT PRIMARY KEY)')
    cur.execute('CREATE TABLE IF NOT EXISTS blacklist (user_id BIGINT PRIMARY KEY)')
    cur.execute('CREATE TABLE IF NOT EXISTS new_files (id SERIAL PRIMARY KEY, category TEXT, file_name TEXT, file_id TEXT)')
    conn.commit()
    cur.close()
    conn.close()

# --- 3. Middlewares & Checks ---
async def check_auth(u_id, context):
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM blacklist WHERE user_id = %s", (u_id,))
    ban = cur.fetchone()
    cur.close(); conn.close()
    if ban: return False
    try:
        m = await context.bot.get_chat_member(CHANNEL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except:
        return False

# --- 4. User Commands ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("INSERT INTO users (user_id, name, username) VALUES (%s, %s, %s) ON CONFLICT (user_id) DO UPDATE SET name=%s, username=%s", (u.id, u.first_name, f"@{u.username}", u.first_name, f"@{u.username}"))
    conn.commit(); cur.close(); conn.close()
    
    if not await check_auth(u.id, context):
        await update.message.reply_text("ကျနော်ရဲ့ MCM Channel ကိုအရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\nJoin ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("Join Channel", url=f"https://t.me/{CHANNEL_ID[1:]}")]]))
        return
    await update.message.reply_text("<b>Welcome ပါဗျာ</b>\n\n<b>Advance File Bot 4.0 ကိုစတင်အသုံးပြုနိုင်ပါပြီ</b>\n\nရယူနိုင်သော File များစရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပေးပါ။\n\nBot အသုံးပြုနည်းကြည့်ရရန် /tutorial ကိုနှိပ်ပေးပါ။", parse_mode='HTML')

async def list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("📦 Addons", callback_data="cat_Addons"), InlineKeyboardButton("🎨 Texture Pack", callback_data="cat_Texture Pack")],
        [InlineKeyboardButton("✨ Shader Pack", callback_data="cat_Shader Pack"), InlineKeyboardButton("🗺️ World/Map", callback_data="cat_World/Map")],
        [InlineKeyboardButton("🎮 MC Version", callback_data="cat_MC Version")]
    ]
    msg = "<b>📂 ဖိုင်အမျိုးအစားများကို ရွေးချယ်ပါ</b>"
    if update.callback_query:
        await update.callback_query.edit_message_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

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

# --- 5. Admin Commands ---
async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    if not update.message.document:
        await update.message.reply_text("❌ ဖိုင်နှင့်တွဲ၍ Caption တွင် <code>/add Category Name</code> ဟု ရိုက်ပို့ပါ။", parse_mode='HTML')
        return
    try:
        cat, name = context.args[0], " ".join(context.args[1:])
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO new_files (category, file_name, file_id) VALUES (%s, %s, %s)", (cat, name, update.message.document.file_id))
        conn.commit(); cur.close(); conn.close()
        await update.message.reply_text(f"✅ သိမ်းဆည်းပြီးပါပြီ - {name}")
    except:
        await update.message.reply_text("❌ ပုံစံမှားနေပါသည်။")

async def remove_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    name = " ".join(context.args)
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("DELETE FROM new_files WHERE file_name = %s", (name,))
    conn.commit(); cur.close(); conn.close()
    await update.message.reply_text(f"🗑️ ဖျက်ပြီးပါပြီ - {name}")

async def user_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    q = update.callback_query
    p = int(q.data.split("_")[1]) if q and q.data.startswith("ul_") else 0
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    cur.execute("SELECT name, username, user_id FROM users LIMIT 20 OFFSET %s", (p*20,))
    users = cur.fetchall()
    cur.close(); conn.close()
    txt = f"👤 <b>Total Users: {total}</b>\n\n"
    for i, u in enumerate(users, p*20+1):
        txt += f"{i}. {u[0]} ({u[1]}) - <code>{u[2]}</code>\n"
    btns = []
    if p > 0: btns.append(InlineKeyboardButton("⬅️ Back", callback_data=f"ul_{p-1}"))
    if (p+1)*20 < total: btns.append(InlineKeyboardButton("Next ➡️", callback_data=f"ul_{p+1}"))
    kb = InlineKeyboardMarkup([btns]) if btns else None
    if q:
        await q.edit_message_text(txt, reply_markup=kb, parse_mode='HTML')
    else:
        await update.message.reply_text(txt, reply_markup=kb, parse_mode='HTML')

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    txt = update.message.text_html.split(None, 1)[1] if len(context.args) > 0 else None
    if not txt: return
    is_group = "gbroadcast" in update.message.text
    conn = get_db_conn(); cur = conn.cursor()
    if is_group: cur.execute("SELECT group_id FROM groups")
    else: cur.execute("SELECT user_id FROM users")
    targets = cur.fetchall()
    cur.close(); conn.close()
    count = 0
    for (tid,) in targets:
        try:
            await context.bot.send_message(tid, txt, parse_mode='HTML')
            count += 1
        except: pass
    await update.message.reply_text(f"✅ {'Groups' if is_group else 'Users'} {count} ဦးထံ ပို့ဆောင်ပြီး။")

async def sms_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        target = context.args[0].replace("@","")
        msg = " ".join(context.args[1:])
        conn = get_db_conn(); cur = conn.cursor()
        if target.isdigit(): uid = int(target)
        else:
            cur.execute("SELECT user_id FROM users WHERE username ILIKE %s", (f"@{target}",))
            res = cur.fetchone()
            uid = res[0] if res else None
        cur.close(); conn.close()
        if uid:
            await context.bot.send_message(uid, f"📩 <b>Owner ဆီမှ စာပြန်လာပါသည်:</b>\n\n{msg}", parse_mode='HTML')
            await update.message.reply_text("✅ ပို့ပြီး။")
    except:
        await update.message.reply_text("❌ ပုံစံမှားနေပါသည်။")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        uid = int(context.args[0])
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO blacklist (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
        conn.commit(); cur.close(); conn.close()
        await update.message.reply_text(f"🚫 User {uid} ကို Ban လိုက်ပါပြီ။")
    except: pass

# --- 6. Handlers ---
async def give_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = " ".join(context.args)
    if not name: return
    found = []
    # (file_database Logic ဒီမှာပါဝင်ပါတယ် - နေရာလွတ်သက်သာစေရန် အကျဉ်းချုပ်ထားခြင်းဖြစ်သည်)
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT file_name, file_id FROM new_files WHERE file_name ILIKE %s", (f"%{name}%",))
    dbf = cur.fetchall(); cur.close(); conn.close()
    for r in dbf: found.append((r[0], r[1]))
    if found: await update.message.reply_document(found[0][1], caption=found[0][0])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private':
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO groups (group_id) VALUES (%s) ON CONFLICT DO NOTHING", (update.effective_chat.id,))
        conn.commit(); cur.close(); conn.close()
        return
    u = update.effective_user
    if not await check_auth(u.id, context): return
    txt = update.message.text
    if txt and not txt.startswith('/'):
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("SELECT file_name, file_id FROM new_files WHERE file_name ILIKE %s", (f"%{txt}%",))
        dbf = cur.fetchall(); cur.close(); conn.close()
        if dbf: await update.message.reply_document(dbf[0][1], caption=dbf[0][0])

async def btn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data.startswith("ul_"): await user_list(update, context)
    elif q.data == "main": await list_menu(update, context)
    elif q.data.startswith("cat_"):
        cn = q.data.replace("cat_", ""); res = f"<b>📂 {cn}</b>\n\n"
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("SELECT file_name FROM new_files WHERE category = %s", (cn,))
        dbf = cur.fetchall(); cur.close(); conn.close()
        for r in dbf: res += f"• <code>{r[0]}</code>\n"
        await q.edit_message_text(res, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main")]]), parse_mode='HTML')

# --- 7. Runner ---
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

if __name__ == '__main__':
    main()
