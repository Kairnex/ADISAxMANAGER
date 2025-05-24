import logging
from datetime import datetime, timedelta
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatPermissions, Update
from telegram.ext import ContextTypes
from utils import is_admin, is_sudo, is_authorized, warn_user, remove_warning, reset_warning, get_warning_count
from config import MAINTENANCE_MODE, SUDO_USERS, CHANNEL_LINK, SUPPORT_GROUP_LINK
from db import auth_col

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if MAINTENANCE_MODE and not is_sudo(update.effective_user.id, SUDO_USERS):
        await update.message.reply_text("🚧 Bot is under maintenance. Please check back later.")
        return

    buttons = [[
        InlineKeyboardButton("📚 Help", callback_data="help"),
        InlineKeyboardButton("📢 Channel", url=CHANNEL_LINK),
        InlineKeyboardButton("🛠 Support", url=SUPPORT_GROUP_LINK)
    ]]
    await update.message.reply_text(
        "👋 Welcome to EditGuard Bot!\nI protect your group from suspicious edited messages.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

async def help_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text("""
🛡 Available Commands:

/auth - Authorize a user
/unauth - Revoke a user's authorization
/authlist - List authorized users
/broadcast - Broadcast message (sudo only)
/maintenance - Toggle maintenance mode (sudo only)

I delete edited messages unless you're authorized!
""")

async def edited_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE
    if MAINTENANCE_MODE:
        return
    message = update.edited_message
    chat_id = message.chat_id
    user_id = message.from_user.id

    if is_authorized(chat_id, user_id):
        return

    await message.delete()
    count = warn_user(chat_id, user_id)

    buttons = [
        [InlineKeyboardButton("❌ Remove Warning", callback_data=f"remwarn:{user_id}")]
    ]
    await context.bot.send_message(chat_id,
                             f"⚠️ @{message.from_user.username or message.from_user.first_name}, you are not allowed to edit messages. Warning {count}/3",
                             reply_markup=InlineKeyboardMarkup(buttons))

    if count >= 3:
        await context.bot.restrict_chat_member(chat_id, user_id, ChatPermissions(can_send_messages=False),
                                         until_date=datetime.utcnow() + timedelta(minutes=10))
        reset_warning(chat_id, user_id)
        await context.bot.send_message(chat_id, f"🔇 User @{message.from_user.username or message.from_user.first_name} has been muted for 10 minutes.")

async def remove_warning_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    chat = query.message.chat
    user_id = int(query.data.split(":")[1])

    if not is_admin(query.from_user.id, chat):
        await query.answer("Only admins can remove warnings.", show_alert=True)
        return

    remove_warning(chat.id, user_id)
    await query.edit_message_text("✅ Warning removed by admin.")

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        await update.message.reply_text("Only group admins can authorize users.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the user you want to authorize.")
        return

    user = update.message.reply_to_message.from_user
    auth_col.update_one({"chat_id": update.effective_chat.id, "user_id": user.id}, {"$set": {"username": user.username}}, upsert=True)
    await update.message.reply_html(f"✅ Authorized {user.mention_html()}")

async def unauth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        await update.message.reply_text("Only group admins can unauthorize users.")
        return

    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to the user you want to unauthorize.")
        return

    user = update.message.reply_to_message.from_user
    auth_col.delete_one({"chat_id": update.effective_chat.id, "user_id": user.id})
    await update.message.reply_html(f"❌ Unauthorized {user.mention_html()}")

async def authlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id, update.effective_chat):
        await update.message.reply_text("Only group admins can use this.")
        return

    users = auth_col.find({"chat_id": update.effective_chat.id})
    text = "👤 Authorized Users:\n" + "\n".join([f"@{user.get('username', 'N/A')} ({user['user_id']})" for user in users])
    await update.message.reply_text(text or "No users authorized.")

async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_sudo(update.effective_user.id, SUDO_USERS):
        await update.message.reply_text("Only sudo users can use this.")
        return

    text = update.message.text.split(None, 1)
    if len(text) < 2:
        await update.message.reply_text("Usage: /broadcast <message>")
        return

    for chat in auth_col.distinct("chat_id"):
        try:
            await context.bot.send_message(chat_id=chat, text=text[1])
        except Exception as e:
            logger.error(f"Failed to send message to {chat}: {e}")

async def maintenance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global MAINTENANCE_MODE
    if not is_sudo(update.effective_user.id, SUDO_USERS):
        await update.message.reply_text("Only sudo users can toggle maintenance mode.")
        return

    MAINTENANCE_MODE = not MAINTENANCE_MODE
    status = "ON" if MAINTENANCE_MODE else "OFF"
    await update.message.reply_text(f"🚧 Maintenance mode is now {status}.")
