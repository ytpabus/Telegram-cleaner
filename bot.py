import os
import time
import threading
import urllib.request
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

BOT_TOKEN = os.environ["BOT_TOKEN"]

last_activity = {"time": datetime.now(timezone.utc), "detail": "starting up"}
_lock = threading.Lock()


def record_activity(detail):
    with _lock:
        last_activity["time"] = datetime.now(timezone.utc)
        last_activity["detail"] = detail


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        with _lock:
            ts = last_activity["time"].isoformat()
            detail = last_activity["detail"]
        body = f"OK - last activity: {detail} at {ts}".encode()
        self.send_response(200)
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):
        pass


def run_health_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


def run_heartbeat(interval_seconds=300):
    while True:
        time.sleep(interval_seconds)
        with _lock:
            detail = last_activity["detail"]
        print(f"Heartbeat: bot alive, last activity: {detail}")


def run_self_ping(interval_seconds=600):
    url = os.environ.get("RENDER_EXTERNAL_URL")
    if not url:
        print("Self-ping skipped: RENDER_EXTERNAL_URL not set")
        return
    while True:
        time.sleep(interval_seconds)
        try:
            urllib.request.urlopen(url, timeout=10)
            print("Self-ping OK")
        except Exception as e:
            print(f"Self-ping FAILED: {e}")


async def delete_join_leave(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message

    if not msg:
        return

    if msg.new_chat_members:
        try:
            await msg.delete()
            print("JOIN removed")
            record_activity("removed JOIN message")
        except Exception:
            print("FAILED to remove JOIN")
            record_activity("FAILED to remove JOIN message")

    elif msg.left_chat_member:
        try:
            await msg.delete()
            print("LEFT removed")
            record_activity("removed LEFT message")
        except Exception:
            print("FAILED to remove LEFT")
            record_activity("FAILED to remove LEFT message")


threading.Thread(target=run_health_server, daemon=True).start()
threading.Thread(target=run_heartbeat, daemon=True).start()
threading.Thread(target=run_self_ping, daemon=True).start()

app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(
    filters.StatusUpdate.NEW_CHAT_MEMBERS | filters.StatusUpdate.LEFT_CHAT_MEMBER,
    delete_join_leave
))

print("Bot running...")
app.run_polling()
