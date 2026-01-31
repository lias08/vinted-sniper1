# main.py
import os
import discord
from discord.ext import commands
from discord import app_commands

# === ENV VARIABLES ===
# DISCORD_TOKEN -> dein Bot-Token
# DISCORD_GUILD_ID -> ID des Testservers (nur Zahlen, keine Anführungszeichen)
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

# === INTENTS ===
intents = discord.Intents.default()  # für Slash Commands reichen Default Intents
# Wenn du Nachrichten-Inhalt brauchst, aktiviere:
# intents.message_content = True

# === BOT INIT ===
bot = commands.Bot(command_prefix="!", intents=intents)

# === COG / SLASH COMMAND ===
class MyBot(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="start", description="Starte den Bot")  # Slash Command
    async def start(self, interaction: discord.Interaction):
        await interaction.response.send_message("Bot gestartet ✅")

# === SETUP FUNCTION ===
async def setup():
    # Cog hinzufügen
    await bot.add_cog(MyBot(bot))
    # Test-Guild Objekt erstellen
    guild = discord.Object(id=GUILD_ID)
    # Nur für diese Guild synchronisieren (schneller als global)
    await bot.tree.sync(guild=guild)
    print("✅ Slash Commands synchronisiert")

# === EVENTS ===
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

# === START BOT ===
bot.loop.create_task(setup())
bot.run(TOKEN)
