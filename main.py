import discord
from discord.ext import commands
import os

# -------------------------
# Environment Variables
# -------------------------
TOKEN = os.getenv("DISCORD_TOKEN")          # Dein Bot-Token
GUILD_ID = int(os.getenv("DISCORD_GUILD_ID"))  # Die Server-ID, in dem der Bot testen soll

# -------------------------
# Intents
# -------------------------
intents = discord.Intents.default()
# Wenn du Zugriff auf Nachrichteninhalt brauchst, z.B. message commands:
# intents.message_content = True

# -------------------------
# Bot Setup
# -------------------------
bot = commands.Bot(command_prefix="!", intents=intents)

# -------------------------
# On Ready Event
# -------------------------
@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")
    guild = discord.Object(id=GUILD_ID)
    # Synchronisiert alle Slash Commands für diese Guild sofort
    await bot.tree.sync(guild=guild)
    print("✅ Slash Commands synchronisiert")

# -------------------------
# Beispiel Slash Command
# -------------------------
@bot.tree.command(name="start", description="Startet etwas", guild=discord.Object(id=GUILD_ID))
async def start_command(interaction: discord.Interaction):
    await interaction.response.send_message("Bot gestartet!")

@bot.tree.command(name="ping", description="Antwortet mit Pong!", guild=discord.Object(id=GUILD_ID))
async def ping_command(interaction: discord.Interaction):
    await interaction.response.send_message("Pong!")

# -------------------------
# Run Bot
# -------------------------
bot.run(TOKEN)
