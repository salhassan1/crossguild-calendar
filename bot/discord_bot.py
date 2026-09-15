import os
import sqlite3
from datetime import timezone
from discord import app_commands

import discord
from discord.ext import commands
from dotenv import load_dotenv
from bot.discord_bot import bot

# ============================================================
# CONFIGURATION
# ============================================================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "events.db")

# Charger le fichier .env AVANT de lire les variables d'environnement
load_dotenv(os.path.join(BASE_DIR, ".env"))
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0"))

CALENDAR_URL = os.getenv(
    "CALENDAR_URL",
    "http://127.0.0.1:5000"
)
# ============================================================
# BOT DISCORD
# ============================================================

intents = discord.Intents.default()
intents.guild_scheduled_events = True

bot = commands.Bot(
    command_prefix="!",
    intents=intents
)

@bot.tree.command(
    name="calendrier",
    description="Affiche le calendrier des événements CrossGuild"
)
async def calendrier(interaction: discord.Interaction):

    embed = discord.Embed(
        title="📅 Calendrier CrossGuild",
        description=(
            "Retrouvez tous les événements programmés "
            "du serveur dans notre calendrier."
        ),
        color=discord.Color.red()
    )

    embed.set_footer(
        text="CrossGuild • Calendrier des événements"
    )

    view = discord.ui.View()

    button = discord.ui.Button(
        label="📅 Ouvrir le calendrier",
        style=discord.ButtonStyle.link,
        url=CALENDAR_URL
    )

    view.add_item(button)

    await interaction.response.send_message(
        embed=embed,
        view=view
    )
    
# ============================================================
# BASE DE DONNÉES
# ============================================================

def get_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS events (
                id TEXT PRIMARY KEY,
                guild_id TEXT NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                start_time TEXT NOT NULL,
                end_time TEXT,
                image_url TEXT,
                event_url TEXT,
                status TEXT,
                location TEXT,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()

   
# ============================================================
# OUTILS
# ============================================================

def get_event_image(event):
    """
    Récupère l'image de couverture de l'événement.
    """

    cover_image = getattr(event, "cover_image", None)

    if cover_image:
        return cover_image.url

    return None


def get_event_location(event):
    """
    Récupère le lieu d'un événement externe.
    """

    metadata = getattr(event, "entity_metadata", None)

    if metadata:
        return getattr(metadata, "location", None)

    return None


def event_to_data(event):
    """
    Transforme un événement Discord
    en données compatibles avec SQLite.
    """

    start = event.start_time.astimezone(
        timezone.utc
    ).isoformat()

    end = None

    if event.end_time:
        end = event.end_time.astimezone(
            timezone.utc
        ).isoformat()

    image = get_event_image(event)

    location = get_event_location(event)

    return (
        str(event.id),
        str(event.guild_id),
        event.name,
        event.description,
        start,
        end,
        image,
        event.url,
        str(event.status),
        location,
    )


# ============================================================
# BASE DE DONNÉES : AJOUT / MODIFICATION
# ============================================================

def upsert_event(event):

    data = event_to_data(event)

    with get_db() as conn:

        conn.execute("""
            INSERT INTO events (
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
            )

            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)

            ON CONFLICT(id) DO UPDATE SET

                name = excluded.name,
                description = excluded.description,
                start_time = excluded.start_time,
                end_time = excluded.end_time,
                image_url = excluded.image_url,
                event_url = excluded.event_url,
                status = excluded.status,
                location = excluded.location,
                updated_at = CURRENT_TIMESTAMP
        """, data)

        conn.commit()


# ============================================================
# SUPPRESSION
# ============================================================

def delete_event(event_id):

    with get_db() as conn:

        conn.execute(
            "DELETE FROM events WHERE id = ?",
            (str(event_id),)
        )

        conn.commit()


# ============================================================
# SYNCHRONISATION COMPLÈTE
# ============================================================

async def sync_events(guild):

    print("Synchronisation des événements Discord...")

    events = await guild.fetch_scheduled_events(
        with_counts=True
    )

    for event in events:

        if event.status.name.lower() in ("cancelled", "canceled"):
            delete_event(event.id)
            continue

        upsert_event(event)

    print(
        f"{len(events)} événement(s) synchronisé(s)."
    )


# ============================================================
# BOT : CONNEXION
# ============================================================

@bot.event
async def on_ready():

    init_db()

    await bot.tree.sync()

    print()
    print("===================================")
    print(f"Connecté : {bot.user}")
    print("===================================")

    guild = bot.get_guild(GUILD_ID)

    if guild is None:

        print(
            "❌ Serveur introuvable."
        )

        print(
            "Vérifie DISCORD_GUILD_ID "
            "et l'installation du bot."
        )

        return

    print(
        f"Serveur détecté : {guild.name}"
    )

    await sync_events(guild)


# ============================================================
# NOUVEL ÉVÉNEMENT
# ============================================================

@bot.event
async def on_scheduled_event_create(event):

    if event.guild_id != GUILD_ID:
        return

    upsert_event(event)

    print(
        f"🟢 Événement ajouté : {event.name}"
    )


# ============================================================
# ÉVÉNEMENT MODIFIÉ
# ============================================================

@bot.event
async def on_scheduled_event_update(
    before,
    after
):

    if after.guild_id != GUILD_ID:
        return

    # Vérifie si l'événement a été annulé
    if after.status.name.lower() in ("cancelled", "canceled"):

        delete_event(after.id)

        print(
            f"🔴 Événement annulé et supprimé : {after.name}"
        )

        return

    # Sinon, c'est une modification normale
    upsert_event(after)

    print(
        f"🟡 Événement mis à jour : {after.name}"
    )


# ============================================================
# ÉVÉNEMENT SUPPRIMÉ
# ============================================================

@bot.event
async def on_scheduled_event_delete(event):

    if event.guild_id != GUILD_ID:
        return

    delete_event(event.id)

    print(
        f"🔴 Événement supprimé : {event.name}"
    )


# ============================================================
# DÉMARRAGE
# ============================================================

if __name__ == "__main__":

    if not TOKEN:
        raise RuntimeError(
            "DISCORD_TOKEN est manquant dans .env"
        )

    if not GUILD_ID:
        raise RuntimeError(
            "DISCORD_GUILD_ID est manquant dans .env"
        )

    init_db()

    bot.run(TOKEN)