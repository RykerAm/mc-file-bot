import os
import json
import asyncio
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# --- Flask Server ---
app = Flask('')
@app.route('/')
def home(): return "Advance File Bot is Online!"

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()

# --- Configuration ---
TOKEN = '8512047741:AAFGZ0dCg8MQ6hoUUBja-6dCchdgHkoIc70'
OWNER_ID = 6112249043
CHANNEL_ID = -1002447990520 
PUBLIC_CHANNEL = '@MinecraftMyanmarMCM'
DATA_FILE = "data.json"

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f: return json.load(f)
    return {"files": [], "users": {}, "groups": []}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f, indent=4)

# --- Auth ---
async def check_auth(u_id, context):
    try:
        m = await context.bot.get_chat_member(PUBLIC_CHANNEL, u_id)
        return m.status in ['member', 'administrator', 'creator']
    except: return False

# --- Admin Commands ---

async def fadd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        args = " ".join(context.args).split("|")
        cat, name, mid = args[0].strip(), args[1].strip(), args[2].strip()
        data = load_data()
        data["files"].append({"cat": cat, "name": name, "msg_id": mid})
        save_data(data)
        await update.message.reply_text(f"✅ **မှတ်တမ်းတင်ပြီးပါပြီ!**\n📂 Cat: {cat}\n📄 Name: {name}\n🆔 ID: `{mid}`", parse_mode='Markdown')
    except: await update.message.reply_text("သုံးစွဲပုံ: `/fadd Cat | Name | ID`", parse_mode='Markdown')

async def del_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    name = " ".join(context.args).strip()
    data = load_data(); initial_len = len(data["files"])
    data["files"] = [f for f in data["files"] if f["name"].lower() != name.lower()]
    if len(data["files"]) < initial_len:
        save_data(data); await update.message.reply_text(f"🗑 **'{name}' ကို ဖျက်လိုက်ပါပြီ။**")
    else: await update.message.reply_text("❌ ရှာမတွေ့ပါ။")

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    data = load_data(); u_ids = list(data["users"].keys())
    page = 0
    current_u = u_ids[page*30:(page+1)*30]
    # HTML သုံးလိုက်လို့ Username ထဲက _ တွေ လုံးဝ မပျောက်တော့ပါဘူး
    txt = f"📊 <b>Stats</b>\n👥 Users: {len(u_ids)}\n📂 Files: {len(data['files'])}\n\n<b>User List (Page 1):</b>\n"
    for uid in current_u: 
        txt += f"- {data['users'][uid]} (<code>{uid}</code>)\n"
    kb = [[InlineKeyboardButton("Next ➡️", callback_data=f"sp_{page+1}")]] if len(u_ids) > 30 else []
    await update.message.reply_text(txt, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    msg = " ".join(context.args)
    if not msg: return
    data = load_data(); count = 0
    s_msg = await update.message.reply_text("⏳ ပေးပို့နေပါသည်...")
    for uid in data["users"].keys():
        try: await context.bot.send_message(int(uid), msg); count += 1
        except: pass
    await s_msg.edit_text(f"✅ ပေးပို့ပြီးစီး!\n👤 လက်ခံရရှိသူ: {count}")

async def gbroadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    msg = " ".join(context.args)
    if not msg: return
    data = load_data(); count = 0
    s_msg = await update.message.reply_text("⏳ Group များသို့ ပို့နေပါသည်...")
    for gid in data.get("groups", []):
        try: await context.bot.send_message(gid, msg); count += 1
        except: pass
    await s_msg.edit_text(f"✅ Group {count} ခုသို့ ပို့ပြီးပါပြီ။")

async def sms(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    try:
        args = " ".join(context.args).split("|")
        target, text = args[0].strip(), args[1].strip()
        data = load_data(); t_id = None
        if target.startswith("@"):
            for uid, uname in data["users"].items():
                if uname == target: t_id = int(uid); break
        else: t_id = int(target)
        if t_id:
            await context.bot.send_message(t_id, text)
            await update.message.reply_text(f"✅ {target} ဆီ ပို့ပြီးပါပြီ။")
    except: await update.message.reply_text("`/sms @user | စာ`", parse_mode='Markdown')

# --- User & Search Logic ---

async def tutorial(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = """Advance File Bot အသုံးပြုနည်း tutorial

ဒီ Bot ကို အသုံးပြုပြီး Minecraft Bedrock Addon File တွေကို လွယ်လွယ်ကူကူ ရှာဖွေရယူနိုင်ပါတယ်ဗျ။

---

၁။ Bot ထဲမှာ တိုက်ရိုက်ရှာနည်း

1️⃣ File ကိုတိုက်ရိုက်ရှာရန်
 Bot ရဲ့ Chat ထဲမှာ ဖိုင်နာမည်ကို ရိုက်ပို့လိုက်ရုံပါပဲ။
 ဥပမာ- `One Piece Addon` သို့မဟုတ် `one piece`
   
2️⃣အမျိုးအစားအလိုက်ကြည့်ရန်:
   `/list` Command ကို နှိပ်ပြီး Addon, Texture စတဲ့ ခလုတ်တွေထဲကနေဝင်ရောက်ကြည့်ရှုနိုင်ပါတယ်။

---

၂။ Group ထဲမှာ File တောင်းနည်း (Group Only)

Group ထဲမှာဆိုရင် စာတွေအများကြီး ရိုက်နေကြတာမို့ Bot က အလိုအလျောက် မရှာပေးပါဘူး။ `/give` command ကို သုံးပြီး ရှာရပါမယ်။

အသုံးပြုပုံ: `/give [ဖိုင်နာမည်]`
ဥပမာ- `/give Naruto Addon`_

---

၃။ Bot ဆီမှာ မတင်ရသေးသော file တင်ခိုင်းရန် and Feedback

Bot ဆီမှာမရှိ့သေးတဲ့ file တင်ခိုင်းရန် `/req [ဖိုင်နာမည်]`
  _ဥပမာ- `/req Fps boost တင်ပေးပါ`_
  
FeedBack ပြောရန်: /fb [စာသား]`
  _ဥပမာ- `/fb bot က ဖိုင်ရှာမပေးဘူး ဖြစ်နေတယ်`_

သတိပြုရန်: File များ ရယူနိုင်ရန်အတွက် @MinecraftMyanmarMCM Channel ကို မဖြစ်မနေ Join ထားရပါမယ်ဗျာ။"""

    await update.message.reply_text(txt, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user; data = load_data()
    uname = f"@{user.username}" if user.username else user.first_name
    data["users"][str(user.id)] = uname
    if update.effective_chat.type != 'private' and update.effective_chat.id not in data["groups"]:
        data["groups"].append(update.effective_chat.id)
    save_data(data)
    
    if not await check_auth(user.id, context):
        return await update.message.reply_text(f"ကျနော်ရဲ့ MCM Channel ကိုအရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\nJoin ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ {PUBLIC_CHANNEL}")
        
    await update.message.reply_text(f" Welcome ပါ {user.first_name}!\n\nAdvance File Bot ကိုစတင်အသုံးပြုနိုင်ပါပြီ\n\nရယူနိုင်သော File များစရင်းကိုကြည့်ရန် /list ကိုနှိပ်ပေးပါ။\n\nBot အသုံးပြုနည်းကြည့်ရရန် /tutorial ကိုနှိပ်ပေးပါ။")

async def give_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type == 'private': return
    query = " ".join(context.args).lower()
    if not await check_auth(update.effective_user.id, context):
        return await update.message.reply_text(f"ကျနော်ရဲ့ MCM Channel ကိုအရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\nJoin ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ {PUBLIC_CHANNEL}")
    data = load_data()
    found = [f for f in data["files"] if query in f["name"].lower()]
    for f in found:
        try:
            await context.bot.copy_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=int(f["msg_id"]), caption=f"ဒီမှာပါ: {f['name']}")
        except:
            pass

async def list_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = load_data()
    cats = sorted(list(set([f["cat"] for f in data["files"]])))
    kb = [[InlineKeyboardButton(c, callback_data=f"cat_{c}")] for c in cats]
    txt = "<b>📂 Categories</b>" if kb else "ဖိုင်များ မရှိသေးပါ။"
    if update.callback_query: await update.callback_query.edit_message_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')
    else: await update.message.reply_text(txt, reply_markup=InlineKeyboardMarkup(kb), parse_mode='HTML')

async def btn_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query; await q.answer(); data = load_data()
    if q.data.startswith("sp_"):
        page = int(q.data.split("_")[1]); u_ids = list(data["users"].keys())
        current = u_ids[page*30:(page+1)*30]
        txt = f"📊 <b>User List (Page {page+1}):</b>\n"
        for uid in current: 
            txt += f"- {data['users'][uid]} (<code>{uid}</code>)\n"
        kb = []
        nav = []
        if page > 0: nav.append(InlineKeyboardButton("⬅️ Back", callback_data=f"sp_{page-1}"))
        if (page+1)*30 < len(u_ids): nav.append(InlineKeyboardButton("Next ➡️", callback_data=f"sp_{page+1}"))
        if nav: kb.append(nav)
        await q.edit_message_text(txt, parse_mode='HTML', reply_markup=InlineKeyboardMarkup(kb))
    elif q.data.startswith("cat_"):
        cat = q.data.replace("cat_", "")
        files = [f for f in data["files"] if f["cat"] == cat]
        txt = f"<b>📂 {cat}:</b>\n\n"
        for f in files: txt += f"• <code>{f['name']}</code>\n"
        await q.edit_message_text(txt, reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data="back")]]), parse_mode='HTML')
    elif q.data == "back": await list_menu(update, context)

async def search_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_chat.type != 'private' or not update.message.text: return
    query = update.message.text.lower()
    if not await check_auth(update.effective_user.id, context):
        return await update.message.reply_text(f"ကျနော်ရဲ့ MCM Channel ကိုအရင် Join ပြီးမှ Bot ကိုအသုံးပြုလို့ရမှာပါဗျ။\n\nJoin ပြီးပါက /start ကိုပြန်နှိပ်ပေးပါ {PUBLIC_CHANNEL}")
    data = load_data()
    found = [f for f in data["files"] if query in f["name"].lower() or f["name"].lower() in query]
    for f in found:
        try:
            # 📂 ဒီနေရာမှာ Channel ထဲက Message ကို စနစ်တကျ Copy ကူးပြီး ပို့ပေးအောင် ပြင်ဆင်လိုက်ပါပြီ
            await context.bot.copy_message(chat_id=update.effective_chat.id, from_chat_id=CHANNEL_ID, message_id=int(f["msg_id"]), caption=f"ဒီမှာပါ: {f['name']}")
        except:
            pass

async def get_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID: return
    f_id = update.message.document.file_id if update.message.document else update.message.video.file_id
    await update.message.reply_text(f"✅ **File ID လက်ခံရရှိသည်:**\n`{f_id}`", parse_mode='Markdown')

async def req_fb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user; msg = " ".join(context.args)
    if not msg: return
    label = "🔔 Request" if update.message.text.startswith("/req") else "⚠️ Feedback"
    await context.bot.send_message(OWNER_ID, f"{label} From {user.first_name} (@{user.username}):\n{msg}")
    await update.message.reply_text("✅ Owner ထံ ပို့ပြီးပါပြီ။")

def main():
    keep_alive()
    bot = Application.builder().token(TOKEN).build()
    bot.add_handler(CommandHandler("start", start))
    bot.add_handler(CommandHandler("stats", stats))
    bot.add_handler(CommandHandler("tutorial", tutorial))
    bot.add_handler(CommandHandler("fadd", fadd))
    bot.add_handler(CommandHandler("del", del_file))
    bot.add_handler(CommandHandler("broadcast", broadcast))
    bot.add_handler(CommandHandler("gbroadcast", gbroadcast))
    bot.add_handler(CommandHandler("sms", sms))
    bot.add_handler(CommandHandler("give", give_command))
    bot.add_handler(CommandHandler("list", list_menu))
    bot.add_handler(CommandHandler("req", req_fb))
    bot.add_handler(CommandHandler("fb", req_fb))
    bot.add_handler(CallbackQueryHandler(btn_handler))
    bot.add_handler(MessageHandler(filters.Document.ALL | filters.VIDEO, get_id))
    bot.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, search_file))
    bot.run_polling()

if __name__ == '__main__': main()
