import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["8755049163:AAGg9a5ExYGoWU4pOhHP8lX-yY7beFcjCe0"]

async def delete_join_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    if not msg:
        return

    if msg.new_chat_members:
        try:
            await msg.delete()
            print("JOIN removed")
        except Exception:
            print("FAILED to remove JOIN")

    elif msg.left_chat_member:
        try:
            await msg.delete()
            print("LEFT removed")
        except Exception:
            print("FAILED to remove LEFT")

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
    delete_join_leave
))

print("Bot running...")
app.run_polling()