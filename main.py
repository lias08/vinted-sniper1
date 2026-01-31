# main.py
import os
import discord
from discord.ext import commands
from discord import app_commands

# === ENV VARIABLES ===
TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))

# === INTENTS ===
intents = discord.Intents.default()

# === BOT INIT ===
class MyBot(commands.Bot):
    def __init__(self):
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self):
        # Cog hinzufügen
        await self.add_cog(MyCog(self))
        # Nur Test-Guild synchronisieren
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print("✅ Slash Commands synchronisiert")

bot = MyBot()

# === COG / SLASH COMMAND ===
class MyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="start", description="Starte den Bot")
    async def start(self, interaction: discord.Interaction):
        await interaction.response.send_message("Bot gestartet ✅")

# === EVENTS ===
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

# === START BOT ===
bot.run(TOKEN)
