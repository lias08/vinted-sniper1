import os
import asyncio
import discord
from discord import app_commands
from sniper import VintedSniper

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 123456789012345678  # 👈 DEINE SERVER ID HIER

class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.snipers = {}

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print("✅ Slash Commands GUILD-synchronisiert")

bot = Bot()

@bot.tree.command(
    name="start",
    description="Starte Vinted Sniper im aktuellen Channel",
    guild=discord.Object(id=GUILD_ID)
)
async def start(interaction: discord.Interaction, url: str):
    channel = interaction.channel

    if channel.id in bot.snipers:
        await interaction.response.send_message(
            "⚠️ In diesem Channel läuft bereits ein Sniper.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "🎯 Sniper gestartet in diesem Channel",
        ephemeral=True
    )

    sniper = VintedSniper(url)

    async def runner():
        while True:
            items = sniper.fetch_items()
            for item in items:
                embed = discord.Embed(
                    title=item["title"],
                    url=item["url"],
                    color=0x2ecc71
                )
                embed.add_field(name="🏷 Marke", value=item["brand"], inline=True)
                embed.add_field(
                    name="💶 Preis",
                    value=f'{item["price"]} {item["currency"]}',
                    inline=True
                )
                embed.add_field(name="✨ Zustand", value=item["condition"], inline=True)
                embed.add_field(name="⏰ Hochgeladen", value=item["created"], inline=False)

                if item["image"]:
                    embed.set_thumbnail(url=item["image"])

                await channel.send(embed=embed)
                await asyncio.sleep(0.5)  # ⏱️ PAUSE NACH JEDER NACHRICHT

            await asyncio.sleep(1)

    bot.snipers[channel.id] = asyncio.create_task(runner())

@bot.tree.command(
    name="stop",
    description="Stoppe Sniper in diesem Channel",
    guild=discord.Object(id=GUILD_ID)
)
async def stop(interaction: discord.Interaction):
    channel = interaction.channel

    task = bot.snipers.pop(channel.id, None)
    if task:
        task.cancel()
        await interaction.response.send_message("🛑 Sniper gestoppt", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Kein Sniper aktiv", ephemeral=True)

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

bot.run(TOKEN)
