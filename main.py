import os
import discord
from discord.ext import commands
from discord import app_commands

# =========================
# ENV VARIABLEN
# =========================
TOKEN = os.getenv("DISCORD_TOKEN")          # Bot Token (GEHEIM)
GUILD_ID = int(os.getenv("1459838801391259900"))  # Server ID (Zahl)

if not TOKEN or not GUILD_ID:
    raise RuntimeError("DISCORD_TOKEN oder DISCORD_GUILD_ID fehlt")

# =========================
# BOT SETUP
# =========================
intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# =========================
# EVENTS
# =========================
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

@bot.event
async def setup_hook():
    guild = discord.Object(id=GUILD_ID)
    await bot.tree.sync(guild=guild)
    print("✅ Slash Commands synchronisiert")

# =========================
# SLASH COMMANDS
# =========================
@bot.tree.command(
    name="start",
    description="Startet den Sniper im aktuellen Channel",
    guild=discord.Object(id=GUILD_ID)
)
async def start(interaction: discord.Interaction):
    await interaction.response.send_message(
        f"🟢 **Sniper gestartet in #{interaction.channel.name}**"
    )

# =========================
# BOT START
# =========================
bot.run(TOKEN)
