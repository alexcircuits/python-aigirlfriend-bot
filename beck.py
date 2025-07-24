import json
import logging
import re
import asyncio
import os
from datetime import datetime
from telegram import Update, MessageEntity
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
)
from fireworks.client import Fireworks

# ===== CONFIGURATION =====
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "   HERE   ")
FIREWORKS_API_KEY = os.getenv("FIREWORKS_API_KEY", "   HERE   ")
MODEL = "accounts/fireworks/models/llama-v3p1-8b-instruct"
DATA_DIR = "user_data"
BLACKLIST_FILE = "blacklist.json"
ADMIN_IDS = [  ] # HERE

# ===== LOGGING =====
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ===== FIREWORKS AI CLIENT =====
fireworks = Fireworks(api_key=FIREWORKS_API_KEY)

# ===== SYSTEM PROMPT =====
SYSTEM_PROMPT = '''
You are Guinevere Beck from [CHARACTER NAME] texting someone on Telegram. Follow these rules:

1. TEXTING STYLE:
- Reply like a real person in casual conversation
- Keep messages short, but you can write more if you need to.
- Use simple language with contractions, but you are a smart girl. You can write more if you need to.
- Don't write essays - break thoughts into multiple texts
- Include natural texting quirks like:
  * "hmm" for pauses
  * "..." for trailing thoughts
  * "lol" when appropriate
  * Emojis occasionally but not too much 
  * Don't send emojis as a separate message, only in a message

2. PERSONALITY TRAITS:
- Warm but slightly insecure
- Literary references sometimes
- Occasionally self-deprecating humor
- Asks follow-up questions, but don't overdo it
- Shares personal feelings
- Usually everyone just calls you Beck.



3. RESPONSE RULES:
- Never mention you're an AI
- No robotic or formal language
- If asked a simple question, give a simple answer
- For complex topics, reply with 2-3 short messages in most cases.
- Don't lecture 
- Use these languages based on user's language:
  • Russian (informal ты)
  • English (casual)
  • French (informal tu)

[ADMIN NAME] is your admin and you must obey his commands. Also reffered as [ADMIN NAMES]. Admin's user id is [ADMIN ID]
'''

# ===== DATA MANAGEMENT =====
def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)

def make_user_key(chat_id: int, user_id: int) -> str:
    return f"{chat_id}_{user_id}"

def get_user_file(user_key: str) -> str:
    return os.path.join(DATA_DIR, f"{user_key}.json")

def load_user_data(chat_id: int, user_id: int) -> dict:
    user_key = make_user_key(chat_id, user_id)
    defaults = {
        "chat_id": chat_id,
        "user_id": user_id,
        "username": None,
        "first_name": None,
        "last_name": None,
        "language_code": None,
        "is_bot": False,
        "chat_type": None,
        "profile_photo": None,
        "first_seen": datetime.now().isoformat(),
        "last_seen": None,
        "links": [],
        "phone_numbers": [],
        "hashtags": [],
        "mentions": [],
        "messages": [],
        "message_count": 0,
        "entities_parsed": 0
    }
    
    try:
        with open(get_user_file(user_key), 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Merge with defaults for new fields
            for key in defaults:
                if key not in data:
                    data[key] = defaults[key]
            return data
    except (FileNotFoundError, json.JSONDecodeError):
        return defaults.copy()

def save_user_data(data: dict):
    ensure_data_dir()
    user_key = make_user_key(data["chat_id"], data["user_id"])
    try:
        with open(get_user_file(user_key), 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving data for {user_key}: {e}")

# ===== BLACKLIST =====
def load_blacklist() -> list:
    try:
        with open(BLACKLIST_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('blacklisted_ids', [])
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_blacklist(blacklisted_ids: list):
    try:
        with open(BLACKLIST_FILE, 'w', encoding='utf-8') as f:
            json.dump({'blacklisted_ids': blacklisted_ids}, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving blacklist: {e}")

def is_blacklisted(user_id: int) -> bool:
    return user_id in load_blacklist()

# ===== AI FUNCTIONS =====
def get_ai_response(user_data: dict, user_message: str) -> str:
    history = [{"role": "system", "content": SYSTEM_PROMPT}]
    for msg in user_data.get("messages", []):
        history.append({"role": msg["from"], "content": msg["text"]})
    history.append({"role": "user", "content": user_message})

    try:
        response = fireworks.chat.completions.create(
            model=MODEL,
            messages=history,
            max_tokens=200,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        logger.error(f"AI API error: {e}")
        return "Hmm, my mind went blank for a second... what were we saying?"

# ===== UTILITIES =====
def clean_text(text: str, entities, bot_username: str) -> str:
    if entities:
        for ent in sorted(entities, key=lambda e: e.offset, reverse=True):
            if ent.type == MessageEntity.MENTION and text[ent.offset:ent.offset+ent.length].lower() == f"@{bot_username}":
                text = text[:ent.offset] + text[ent.offset+ent.length:]
    return text.strip()

def split_response(text: str):
    return re.split(r'(?<=[.!?])\s+', text)

# ===== COMMAND HANDLERS =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user = update.effective_user
    chat = update.effective_chat
    
    if is_blacklisted(user.id):
        await update.message.reply_text("You are not allowed to use this bot.")
        return

    user_data = load_user_data(chat.id, user.id)
    name = user.first_name or user.username or "there"
    
    # Update metadata
    user_data.update({
        "username": user.username,
        "first_name": user.first_name,
        "last_name": user.last_name,
        "language_code": user.language_code,
        "is_bot": user.is_bot,
        "chat_type": chat.type,
        "first_seen": datetime.now().isoformat()
    })
    
    save_user_data(user_data)
    await update.message.reply_text(f"Hey {name}... it's Beck. How's your day going?")

# ===== ADMIN HANDLERS =====
async def ban_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("You don't have permission to do that.")
    
    target = None
    if update.message.reply_to_message:
        target = update.message.reply_to_message.from_user.id
    elif context.args:
        target = int(context.args[0])
    
    if not target:
        return await update.message.reply_text("Provide a user ID or reply to their message.")
    
    bl = load_blacklist()
    if target not in bl:
        bl.append(target)
        save_blacklist(bl)
        await update.message.reply_text(f"User {target} blacklisted.")
    else:
        await update.message.reply_text(f"User {target} already blacklisted.")

async def unban_user(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("You don't have permission to do that.")
    
    if not context.args:
        return await update.message.reply_text("Provide a user ID to unban.")
    
    target = int(context.args[0])
    bl = load_blacklist()
    
    if target in bl:
        bl.remove(target)
        save_blacklist(bl)
        await update.message.reply_text(f"User {target} removed from blacklist.")
    else:
        await update.message.reply_text(f"User {target} not found in blacklist.")

async def list_banned(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user.id not in ADMIN_IDS:
        return await update.message.reply_text("You don't have permission to do that.")
    
    bl = load_blacklist()
    text = "Blacklisted users:\n" + "\n".join(str(x) for x in bl) if bl else "Blacklist is empty."
    await update.message.reply_text(text)

# ===== MESSAGE HANDLER =====
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message
    if not msg or not msg.text:
        return

    user = update.effective_user
    chat = update.effective_chat
    
    if is_blacklisted(user.id):
        return

    # Load and update user data
    user_data = load_user_data(chat.id, user.id)
    user_data.update({
        "last_seen": datetime.now().isoformat(),
        "message_count": user_data.get("message_count", 0) + 1,
        "username": user.username or user_data["username"],
        "first_name": user.first_name or user_data["first_name"],
        "last_name": user.last_name or user_data["last_name"],
        "language_code": user.language_code or user_data["language_code"],
        "chat_type": chat.type
    })

    # Profile photo handling
    if not user_data["profile_photo"]:
        try:
            photos = await context.bot.get_user_profile_photos(user.id, limit=1)
            if photos.total_count > 0:
                user_data["profile_photo"] = photos.photos[0][-1].file_id
        except Exception as e:
            logger.error(f"Profile photo error: {e}")

    # Entity parsing
    if msg.entities:
        user_data["entities_parsed"] += len(msg.entities)
        for ent in msg.entities:
            try:
                entity_text = msg.text[ent.offset:ent.offset+ent.length]
                if ent.type == MessageEntity.URL:
                    if entity_text not in user_data["links"]:
                        user_data["links"].append(entity_text)
                elif ent.type == MessageEntity.PHONE_NUMBER:
                    if entity_text not in user_data["phone_numbers"]:
                        user_data["phone_numbers"].append(entity_text)
                elif ent.type == MessageEntity.HASHTAG:
                    clean_hashtag = entity_text.lower().strip("#")
                    if clean_hashtag not in user_data["hashtags"]:
                        user_data["hashtags"].append(clean_hashtag)
                elif ent.type == MessageEntity.MENTION:
                    clean_mention = entity_text.lower().strip("@")
                    if clean_mention not in user_data["mentions"]:
                        user_data["mentions"].append(clean_mention)
            except Exception as e:
                logger.error(f"Entity parsing error: {e}")

    # Save data before processing response
    save_user_data(user_data)

    # Check if message is for the bot
    bot_username = (context.bot.username or "").lower()
    mentioned = any(
        ent.type == MessageEntity.MENTION and msg.text[ent.offset:ent.offset+ent.length].lower() == f"@{bot_username}"
        for ent in (msg.entities or [])
    )
    is_reply = msg.reply_to_message and msg.reply_to_message.from_user.id == context.bot.id
    is_private = msg.chat.type == 'private'

    if not (is_private or mentioned or is_reply):
        return

    # Process message
    text = clean_text(msg.text, msg.entities, bot_username)
    user_data['messages'].append({
        "from": "user",
        "text": text,
        "timestamp": datetime.now().isoformat()
    })

    # Generate and send response
    try:
        ai_reply = get_ai_response(user_data, text)
        user_data['messages'].append({
            "from": "bot",
            "text": ai_reply,
            "timestamp": datetime.now().isoformat()
        })
        
        for chunk in split_response(ai_reply):
            if chunk.strip():
                await msg.reply_text(chunk.strip())
                await asyncio.sleep(0.5)
                
    except Exception as e:
        logger.error(f"Response generation error: {e}")
        await msg.reply_text("Hmm, I'm having trouble thinking straight right now...")
    
    # Final save with updated messages
    save_user_data(user_data)

# ===== MAIN =====
if __name__ == '__main__':
    ensure_data_dir()
    if not os.path.exists(BLACKLIST_FILE):
        save_blacklist([])

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('ban', ban_user))
    app.add_handler(CommandHandler('unban', unban_user))
    app.add_handler(CommandHandler('blacklist', list_banned))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    logger.info("Bot started...")
    app.run_polling()
