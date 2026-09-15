# Discord Calendar

Calendrier web synchronisé automatiquement avec les événements programmés d'un serveur Discord.

## 1. Prérequis

- Python 3.11+
- Un bot Discord
- Le bot doit être présent sur le serveur

## 2. Installation

### Windows

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

Copier `.env.example` vers `.env`, puis renseigner :

```env
DISCORD_TOKEN=...
DISCORD_GUILD_ID=...
HOST=127.0.0.1
PORT=5000
```

## 3. Lancer le bot

Dans un terminal :

```powershell
python -m bot.discord_bot
```

Le bot synchronise les événements existants au démarrage puis écoute les créations, modifications et suppressions.

## 4. Lancer le site

Dans un deuxième terminal :

```powershell
python -m app.app
```

Ouvrir :

http://127.0.0.1:5000

## Sécurité

Ne jamais publier `.env` ou le token Discord sur GitHub.
