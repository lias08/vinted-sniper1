import discord
from discord.ext import commands
from sniper import VintedSniper
import asyncio
import os

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

tasks = {}

@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online als {bot.user}")

@bot.tree.command(name="start", description="Starte Vinted Suche in diesem Channel")
async def start(interaction: discord.Interaction, url: str):
    channel = interaction.channel

    if channel.id in tasks:
        await interaction.response.send_message(
            "⚠️ In diesem Channel läuft bereits ein Sniper", ephemeral=True
        )
        return

    await interaction.response.send_message(
        "🔍 Suche gestartet in diesem Channel", ephemeral=True
    )

    sniper = VintedSniper(url)

    async def runner():
        while True:
            items = sniper.fetch_items()

            for item in items:
                base_price = sniper.format_price(item)
                total_price = sniper.calc_total_price(base_price)
                image = sniper.get_image(item)

                embed = discord.Embed(
                    title=f"🔥 {item.get('title')}",
                    url=item.get("url") or f"https://www.vinted.de/items/{item['id']}",
                    color=0x09b1ba
                )

                embed.add_field(name="🏷️ Marke", value=item.get("brand_title", "—"), inline=True)
                embed.add_field(name="💶 Preis", value=f"{base_price:.2f} €", inline=True)
                embed.add_field(name="🚚 Gesamt ca.", value=f"{total_price:.2f} €", inline=True)

                embed.add_field(name="✨ Zustand", value=item.get("status", "—"), inline=True)
                embed.add_field(name="📏 Größe", value=item.get("size_title", "—"), inline=True)
                embed.add_field(
                    name="⏰ Hochgeladen",
                    value=sniper.get_uploaded_time(item),
                    inline=True
                )

                if image:
                    embed.set_image(url=image)

                await channel.send(embed=embed)
                await asyncio.sleep(0.5)

            await asyncio.sleep(1)

    task = asyncio.create_task(runner())
    tasks[channel.id] = task

@bot.tree.command(name="stop", description="Stoppt die Suche in diesem Channel")
async def stop(interaction: discord.Interaction):
    channel = interaction.channel
    task = tasks.get(channel.id)

    if task:
        task.cancel()
        del tasks[channel.id]
        await interaction.response.send_message("🛑 Sniper gestoppt", ephemeral=True)
    else:
        await interaction.response.send_message("❌ Kein aktiver Sniper", ephemeral=True)

bot.run(TOKEN)
