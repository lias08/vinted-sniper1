import discord
from discord import app_commands
from discord.ext import commands, tasks
import asyncio
from sniper import VintedSniper

import os

TOKEN = os.getenv("DISCORD_TOKEN")  # Discord Bot Token

intents = discord.Intents.default()
intents.message_content = True  # nötig für Slash Commands

bot = commands.Bot(command_prefix="!", intents=intents)

active_snipers = {}  # Channel-ID -> Task

@bot.event
async def on_ready():
    print(f"✅ Bot online als {bot.user}")
    try:
        synced = await bot.tree.sync()
        print(f"✅ Slash Commands synchronisiert: {len(synced)}")
    except Exception as e:
        print(f"Fehler beim Sync: {e}")

@bot.tree.command(name="start", description="Starte Vinted Sniper in diesem Channel")
@app_commands.describe(url="URL zum Vinted Katalog")
async def start(interaction: discord.Interaction, url: str):
    await interaction.response.send_message(
        "✅ Suche gestartet, Ergebnisse erscheinen hier.", ephemeral=True
    )

    channel = interaction.channel

    if channel.id in active_snipers:
        await channel.send("⚠️ Sniper läuft bereits in diesem Channel!")
        return

    sniper = VintedSniper(url)

    async def sniper_task():
        while True:
            items = sniper.fetch_items()
            for item in items:
                price = item.get("price") or item.get("total_item_price", {}).get("amount", 0)
                status = sniper.get_clean_status(item)
                title = item.get("title")
                url_item = item.get("url") or f"https://www.vinted.de/items/{item.get('id')}"

                embed = discord.Embed(
                    title=f"🔥 {title}",
                    url=url_item,
                    description=f"💶 Preis: {price} €\n✨ Zustand: {status}"
                )
                await channel.send(embed=embed)
                await asyncio.sleep(0.5)  # Pause nach jeder Nachricht

            await asyncio.sleep(1)  # kurze Pause zwischen API-Abfragen

    task = asyncio.create_task(sniper_task())
    active_snipers[channel.id] = task

@bot.tree.command(name="stop", description="Stoppe den Sniper in diesem Channel")
async def stop(interaction: discord.Interaction):
    channel = interaction.channel
    task = active_snipers.get(channel.id)
    if task:
        task.cancel()
        del active_snipers[channel.id]
        await channel.send("🛑 Sniper gestoppt!")
    else:
        await channel.send("❌ Kein aktiver Sniper in diesem Channel.")

bot.run(TOKEN)
