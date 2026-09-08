import os
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def log_message(self, format, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


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


threading.Thread(target=run_health_server, daemon=True).start()

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
    delete_join_leave
))

print("Bot running...")
app.run_polling()
