import os
import sqlite3
from flask import Flask, jsonify, render_template
from dotenv import load_dotenv

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "events.db")

load_dotenv(os.path.join(BASE_DIR, ".env"))

app = Flask(
    __name__,
    template_folder=os.path.join(BASE_DIR, "templates"),
    static_folder=os.path.join(BASE_DIR, "static"),
)

# ============================================================
# BASE DE DONNÉES
# ============================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


# ============================================================
# PAGE PRINCIPALE
# ============================================================

@app.route("/")
def index():
    return render_template("index.html")


# ============================================================
# API DES ÉVÉNEMENTS
# ============================================================

@app.route("/api/events")
def api_events():

    # Si la base n'existe pas encore
    if not os.path.exists(DB_PATH):
        return jsonify([])

    with get_db() as conn:

        rows = conn.execute("""
            SELECT
                id,
                guild_id,
                name,
                description,
                start_time,
                end_time,
                image_url,
                event_url,
                status,
                location,
                updated_at
            FROM events
            ORDER BY start_time
        """).fetchall()

    return jsonify([
        dict(row)
        for row in rows
    ])


# ============================================================
# LANCEMENT DU SERVEUR
# ============================================================

if __name__ == "__main__":

    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "5000"))

    app.run(
        host=host,
        port=port,
        debug=False
    )

def get_events():
    if not os.path.exists(DB_PATH):
        return []

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT id, name, description, start_time, end_time,
               image_url, event_url, status, location
        FROM events
        ORDER BY start_time
    """).fetchall()
    conn.close()

    return [dict(row) for row in rows]


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/events")
def api_events():
    return jsonify(get_events())

if __name__ == "__main__":
    host = os.getenv("HOST", "127.0.0.1")
    port = int(os.getenv("PORT", "5000"))
    app.run(host=host, port=port, debug=True)

@app.route("/api/events")
def get_events():

    with get_db() as conn:

        rows = conn.execute("""
            SELECT *
            FROM events
            ORDER BY start_time
        """).fetchall()

    return jsonify([
        dict(row)
        for row in rows
    ])
