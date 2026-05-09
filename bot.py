import os
import psycopg2
import asyncio
import random
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- 1. Flask Web Server (For Render 24/7 Hosting) ---
app = Flask('')

@app.route('/')
def home():
    return "Advance File V6.3 Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- 2. Configuration & Database Connection ---
TOKEN = '8512047741:AAFGZ0dCg8MQ6hoUUBja-6dCchdgHkoIc70'
OWNER_ID = 6112249043 
CHANNEL_ID = '@MinecraftMyanmarMCM'
DB_URL = "postgres://postgres:T74KeLnyE_%jkGv@db.orxgpwzxdiyfinzqgkaa.supabase.co:5432/postgres"

def get_db_conn():
    # Render အတွက် sslmode='require' ထည့်သွင်းထားသည်
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

# --- 3. Middlewares & Auth ---
async def check_auth(u_id, context):
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT 1 FROM blacklist WHERE user_id = %s", (u_id,))
    ban = cur.fetchone()
    cur.close(); conn.close()
    if ban: return False
    try:
        m = await context.bot.get_chat_member(CHANNEL_ID, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

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
        [InlineKeyboardButton("🎮 MC Version", callback_data="cat_MC Version")],
        [InlineKeyboardButton("🎲 Random File", callback_data="random_file")]
    ]
    txt = "<b>📂 ဖိုင်အမျိုးအစားများကို ရွေးချယ်ပါ</b>"
    if update.callback_query: await update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else: await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

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
        await update.message.reply_text("❌ ဖိုင်နှင့်တွဲ၍ Caption တွင် <code>/add [Category] [Name]</code> ဟု ရိုက်ပို့ပါ။", parse_mode='HTML')
        return
    try:
        cat, name = context.args[0], " ".join(context.args[1:])
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO new_files (category, file_name, file_id) VALUES (%s, %s, %s)", (cat, name, update.message.document.file_id))
        conn.commit(); cur.close(); conn.close()
        await update.message.reply_text(f"✅ သိမ်းဆည်းပြီးပါပြီ - {name}")
    except: await update.message.reply_text("❌ ပုံစံမှားနေပါသည်။ Category နေရာမှာ တစ်လုံးတည်းရှိရပါမယ်။")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    txt = update.message.text_html.split(None, 1)[1] if len(context.args) > 0 else None
    if not txt: return
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT user_id FROM users"); targets = cur.fetchall(); cur.close(); conn.close()
    count = 0
    for (tid,) in targets:
        try: await context.bot.send_message(tid, txt, parse_mode='HTML'); count += 1
        except: pass
    await update.message.reply_text(f"✅ Users {count} ဦးထံ ပို့ဆောင်ပြီး။")

async def sms_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        target = context.args[0].replace("@","")
        msg = " ".join(context.args[1:])
        conn = get_db_conn(); cur = conn.cursor()
        if target.isdigit(): uid = int(target)
        else:
            cur.execute("SELECT user_id FROM users WHERE username ILIKE %s", (f"@{target}",))
            res = cur.fetchone(); uid = res[0] if res else None
        cur.close(); conn.close()
        if uid:
            await context.bot.send_message(uid, f"📩 <b>Owner ဆီမှ စာပြန်လာပါသည်:</b>\n\n{msg}", parse_mode='HTML')
            await update.message.reply_text("✅ ပို့ပြီး။")
    except: await update.message.reply_text("❌ ပုံစံမှားနေပါသည်။")

async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        uid = int(context.args[0])
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("INSERT INTO blacklist (user_id) VALUES (%s) ON CONFLICT DO NOTHING", (uid,))
        conn.commit(); cur.close(); conn.close()
        await update.message.reply_text(f"🚫 User {uid} ကို Ban လိုက်ပါပြီ။")
    except: pass

# --- 6. Message & Button Handlers ---
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text: return
    u_id = update.effective_user.id
    if not await check_auth(u_id, context): return
    
    txt = update.message.text.strip()
    if txt.startswith('/'): return
    
    conn = get_db_conn(); cur = conn.cursor()
    cur.execute("SELECT file_name, file_id FROM new_files WHERE file_name ILIKE %s", (f"%{txt}%",))
    dbf = cur.fetchall(); cur.close(); conn.close()
    
    if dbf:
        # ပထမဆုံးတွေ့တဲ့ဖိုင်ကို ပို့ပေးမည်
        msg = await update.message.reply_document(dbf[0][1], caption=f"ဒီမှာပါ: <b>{dbf[0][0]}</b>", parse_mode='HTML')
        await asyncio.sleep(600); # 10 min
        try: await msg.delete()
        except: pass
    else:
        await update.message.reply_text("❌ ရှာမတွေ့ပါဗျာ။")

async def btn_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer()
    if q.data == "main_list": await list_menu(update, context)
    elif q.data == "random_file":
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("SELECT file_name, file_id FROM new_files ORDER BY RANDOM() LIMIT 1")
        res = cur.fetchone(); cur.close(); conn.close()
        if res:
            doc = await q.message.reply_document(res[1], caption=f"🎲 Random: <b>{res[0]}</b>", parse_mode='HTML')
            await asyncio.sleep(600); await doc.delete()
    elif q.data.startswith("cat_"):
        cn = q.data.replace("cat_", "")
        conn = get_db_conn(); cur = conn.cursor()
        cur.execute("SELECT file_name FROM new_files WHERE category = %s", (cn,))
        dbf = cur.fetchall(); cur.close(); conn.close()
        txt = f"<b>📂 {cn} List:</b>\n\n"
        for r in dbf: txt += f"• <code>{r[0]}</code>\n"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="main_list")]]), parse_mode='HTML')

# --- 7. Runner ---
def main():
    init_db(); keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("list", list_menu))
    bot.add_handler(CommandHandler("fb", fb_req))
    bot.add_handler(CommandHandler("req", fb_req))
    bot.add_handler(CommandHandler("add", add_file))
    bot.add_handler(CommandHandler("broadcast", broadcast))
    bot.add_handler(CommandHandler("Sms", sms_user))
    bot.add_handler(CommandHandler("ban", ban_user))
    bot.add_handler(CallbackQueryHandler(btn_callback))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    bot.run_polling()

if __name__ == '__main__':
    main()
