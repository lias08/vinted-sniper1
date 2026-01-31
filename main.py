import os
import asyncio
import discord
from discord.ext import commands
from vinted_sniper import VintedSniper

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

active_tasks = {}


@bot.event
async def on_ready():
    print("🟢 on_ready wurde aufgerufen")
    synced = await bot.tree.sync()
    print(f"🟢 Slash Commands synced: {len(synced)}")
    print(f"✅ Bot online als {bot.user}")


def build_embed(item):
    embed = discord.Embed(
        title=item.get("title", "Neues Item"),
        url=item.get("url") or f"https://www.vinted.de/items/{item['id']}",
        color=0x09b1ba
    )
    embed.add_field(
        name="Preis",
        value=f"{item.get('price', {}).get('amount', '?')} €",
        inline=True
    )
    return embed


async def run_sniper(url, channel):
    print(f"🟡 Sniper gestartet für Channel {channel.id}")
    sniper = VintedSniper(url)

    await channel.send("🔍 **Suche gestartet**")

    while True:
        items = sniper.fetch_items()
        print(f"🟡 {len(items)} neue Items gefunden")

        for item in items:
            await channel.send(embed=build_embed(item))
            await asyncio.sleep(0.5)

        await asyncio.sleep(1)


@bot.tree.command(name="start", description="Starte eine Vinted Suche in diesem Channel")
async def start(interaction: discord.Interaction, url: str):
    print("🟢 /start Command aufgerufen")

    channel = interaction.channel

    await interaction.response.send_message(
        "✅ Command empfangen, starte Suche…",
        ephemeral=True
    )

    if channel.id in active_tasks:
        print("⚠️ Suche läuft bereits")
        return

    task = asyncio.create_task(run_sniper(url, channel))
    active_tasks[channel.id] = task
    print("🟢 Task gestartet")


bot.run(TOKEN)
