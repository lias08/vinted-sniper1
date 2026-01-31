import os
import asyncio
import discord
from discord import app_commands
from sniper import VintedSniper

TOKEN = os.getenv("DISCORD_TOKEN")

class MyClient(discord.Client):
    def __init__(self):
        intents = discord.Intents.default()
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)
        self.tasks = {}

    async def setup_hook(self):
        await self.tree.sync()
        print("✅ Slash Commands synchronisiert")


client = MyClient()


@client.tree.command(name="start", description="Starte Vinted Suche in diesem Channel")
async def start(interaction: discord.Interaction, url: str):
    print("🟢 /start wurde ausgelöst")  # <- WICHTIGES DEBUG

    channel = interaction.channel

    await interaction.response.send_message(
        "🔍 Suche gestartet in diesem Channel",
        ephemeral=True
    )

    if channel.id in client.tasks:
        await channel.send("⚠️ Sniper läuft hier bereits")
        return

    sniper = VintedSniper(url)

    async def runner():
        while True:
            items = sniper.fetch_items()

            for item in items:
                price_data = item.get("price") or item.get("total_item_price")
                price = (
                    f"{price_data['amount']} {price_data['currency_code']}"
                    if isinstance(price_data, dict)
                    else str(price_data)
                )

                image = None
                photos = item.get("photos", [])
                if photos:
                    image = photos[0]["url"].replace("/medium/", "/full/")

                embed = discord.Embed(
                    title=item.get("title"),
                    url=item.get("url") or f"https://www.vinted.de/items/{item['id']}",
                    color=0x09b1ba
                )

                embed.add_field(name="🏷️ Marke", value=item.get("brand_title", "—"), inline=True)
                embed.add_field(name="💶 Preis", value=price, inline=True)
                embed.add_field(name="✨ Zustand", value=item.get("status", "—"), inline=True)

                if image:
                    embed.set_image(url=image)

                await channel.send(embed=embed)
                await asyncio.sleep(0.5)

            await asyncio.sleep(1)

    task = asyncio.create_task(runner())
    client.tasks[channel.id] = task


@client.event
async def on_ready():
    print(f"✅ Bot online als {client.user}")


client.run(TOKEN)
