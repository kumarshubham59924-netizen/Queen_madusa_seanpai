import os, time, json
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHANNELS = os.getenv("CHANNELS").split(",")  # comma separated list

bot = telebot.TeleBot(BOT_TOKEN, parse_mode="HTML")
DATA_FILE = "users.json"

def load_users():
    try: return set(json.load(open(DATA_FILE)))
    except: return set()

def save_users(u): json.dump(list(u), open(DATA_FILE,"w"))

users = load_users()

def all_joined(uid:int) -> bool:
    for ch in CHANNELS:
        try:
            m = bot.get_chat_member(ch.strip(), uid)
            if m.status not in ("member","administrator","creator"):
                return False
        except:
            return False
    return True

def join_keyboard():
    kb = InlineKeyboardMarkup()
    for i,ch in enumerate(CHANNELS, start=1):
        kb.add(InlineKeyboardButton(f"📢 Channel {i}", url=f"https://t.me/{ch.strip().lstrip('@')}"))
    kb.add(InlineKeyboardButton("☑️ Try Again", callback_data="joined"))
    return kb

@bot.message_handler(commands=['start'])
def start(m):
    photo = "https://i.ibb.co/4pcy7sv/sample.jpg"  # apni image ka direct link yahan daalo
    caption = f"HELLO <b>{m.from_user.first_name}</b> ⚡\n\n👉 Please join all 3 channels and press Try Again!"
    bot.send_photo(m.chat.id, photo=photo, caption=caption, reply_markup=join_keyboard())

@bot.callback_query_handler(func=lambda c: c.data=="joined")
def joined(cb):
    uid = cb.from_user.id
    if all_joined(uid):
        users.add(uid); save_users(users)
        bot.answer_callback_query(cb.id, "✅ Verified")
        bot.send_message(uid, "🎉 Shukriya! Ab se aapko posts milenge.")
    else:
        bot.answer_callback_query(cb.id, "❌ Abhi tak sab join nahi kiya!", show_alert=True)

@bot.channel_post_handler(func=lambda m: True)
def forward_post(msg):
    for uid in list(users):
        try:
            bot.forward_message(uid, msg.chat.id, msg.message_id)
            time.sleep(0.2)
        except: pass

print("Bot running…")
bot.infinity_polling()
