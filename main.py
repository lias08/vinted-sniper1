import os
import asyncio
import discord
from discord.ext import commands
from vinted_sniper import VintedSniper

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

# channel_id -> asyncio.Task
active_tasks = {}


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online als {bot.user}")


def build_embed(item):
    price = item.get("price", {}).get("amount", "?")
    url = item.get("url") or f"https://www.vinted.de/items/{item['id']}"

    embed = discord.Embed(
        title=item.get("title", "Neues Item"),
        url=url,
        color=0x09b1ba
    )

    embed.add_field(name="💶 Preis", value=f"{price} €", inline=True)
    embed.add_field(name="📏 Größe", value=item.get("size_title", "N/A"), inline=True)

    photos = item.get("photos", [])
    if photos:
        embed.set_image(url=photos[0]["url"].replace("/medium/", "/full/"))

    return embed


async def run_sniper(url, channel):
    sniper = VintedSniper(url)
    await channel.send("🔍 **Suche gestartet**")

    while True:
        try:
            items = sniper.fetch_items()
            for item in items:
                await channel.send(embed=build_embed(item))
                await asyncio.sleep(0.5)  # ⏸️ Pause nach Discord-Nachricht

            await asyncio.sleep(1)  # 🔄 fast live
        except Exception as e:
            await channel.send(f"❌ Fehler: `{e}`")
            await asyncio.sleep(5)


@bot.tree.command(name="start", description="Starte eine Vinted-Suche in diesem Channel")
async def start(interaction: discord.Interaction, url: str):
    channel = interaction.channel

    # Prüfen ob in diesem Channel schon eine Suche läuft
    if channel.id in active_tasks:
        await interaction.response.send_message(
            "⚠️ In diesem Channel läuft bereits eine Suche.",
            ephemeral=True
        )
        return

    await interaction.response.send_message(
        "✅ Suche gestartet in diesem Channel.",
        ephemeral=True
    )

    task = asyncio.create_task(run_sniper(url, channel))
    active_tasks[channel.id] = task


@bot.tree.command(name="stop", description="Stoppt die Vinted-Suche in diesem Channel")
async def stop(interaction: discord.Interaction):
    channel = interaction.channel

    task = active_tasks.get(channel.id)
    if not task:
        await interaction.response.send_message(
            "ℹ️ In diesem Channel läuft keine Suche.",
            ephemeral=True
        )
        return

    task.cancel()
    del active_tasks[channel.id]

    await interaction.response.send_message(
        "🛑 Suche in diesem Channel gestoppt.",
        ephemeral=True
    )


bot.run(TOKEN)
