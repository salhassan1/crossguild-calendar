import os
import threading

from app.app import app
from bot.discord_bot import bot


def run_flask():
    port = int(os.getenv("PORT", "5000"))

    app.run(
        host="0.0.0.0",
        port=port,
        debug=False,
        use_reloader=False
    )


if __name__ == "__main__":

    flask_thread = threading.Thread(
        target=run_flask,
        daemon=True
    )

    flask_thread.start()

    bot.run(os.getenv("DISCORD_TOKEN"))