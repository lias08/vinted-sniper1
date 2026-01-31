import os
import asyncio
import discord
from discord import app_commands
from sniper import VintedSniper

TOKEN = os.getenv("DISCORD_TOKEN")
GUILD_ID = 1459838801391259900  # deine Server-ID

class Bot(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.tasks = {}

    async def setup_hook(self):
        guild = discord.Object(id=GUILD_ID)
        await self.tree.sync(guild=guild)
        print("✅ Slash Commands synchronisiert")

bot = Bot()

@bot.tree.command(
    name="start",
    description="Starte Vinted Sniper in diesem Channel",
    guild=discord.Object(id=GUILD_ID)
)
async def start(interaction: discord.Interaction, url: str):
    print("🟢 /start wurde ausgelöst")

    channel = interaction.channel

    await interaction.response.send_message(
        "🎯 Sniper gestartet in diesem Channel",
        ephemeral=True
    )

    sniper = VintedSniper(url)

    async def runner():
        while True:
            items = sniper.fetch_items()
            for item in items:
                price = item.get("price", {})
                price_text = f"{price.get('amount', '?')} €"

                embed = discord.Embed(
                    title=item.get("title", "Kein Titel"),
                    url=item.get("url") or f"https://www.vinted.de/items/{item.get('id')}",
                    color=0x09b1ba
                )

                embed.add_field(name="💶 Preis", value=price_text, inline=True)
                embed.add_field(name="🏷️ Marke", value=item.get("brand_title", "—"), inline=True)
                embed.add_field(name="✨ Zustand", value=item.get("status", "—"), inline=True)

                photos = item.get("photos", [])
                if photos:
                    embed.set_image(url=photos[0]["url"].replace("medium", "full"))

                await channel.send(embed=embed)
                await asyncio.sleep(0.5)

            await asyncio.sleep(2)

    bot.tasks[channel.id] = asyncio.create_task(runner())

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")

bot.run(TOKEN)


