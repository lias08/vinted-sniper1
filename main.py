import os
import asyncio
import discord
from discord.ext import commands
from vinted_sniper import VintedSniper

TOKEN = os.getenv("DISCORD_TOKEN")

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

active_tasks = []


@bot.event
async def on_ready():
    await bot.tree.sync()
    print(f"✅ Bot online als {bot.user}")


def build_embed(item):
    price = item.get("price", {}).get("amount", "?")
    url = item.get("url", f"https://www.vinted.de/items/{item['id']}")

    embed = discord.Embed(
        title=item.get("title", "Neues Item"),
        url=url,
        color=0x09b1ba
    )

    embed.add_field(name="Preis", value=f"{price} €", inline=True)
    embed.add_field(name="Größe", value=item.get("size_title", "N/A"), inline=True)

    photos = item.get("photos", [])
    if photos:
        embed.set_image(url=photos[0]["url"].replace("/medium/", "/full/"))

    return embed


async def run_sniper(url, channel):
    sniper = VintedSniper(url)
    await channel.send("🔍 **Suche gestartet**")

    while True:
        items = sniper.fetch_items()
        for item in items:
            await channel.send(embed=build_embed(item))
            await asyncio.sleep(0.5)  # ⏸️ Discord Pause

        await asyncio.sleep(1)  # 🔄 fast live


@bot.tree.command(name="start", description="Starte eine neue Vinted Suche")
async def start(interaction: discord.Interaction, url: str):
    guild = interaction.guild

    channel = await guild.create_text_channel(
        name="vinted-suche"
    )

    await interaction.response.send_message(
        f"✅ Suche gestartet in {channel.mention}",
        ephemeral=True
    )

    task = asyncio.create_task(run_sniper(url, channel))
    active_tasks.append(task)


bot.run(TOKEN)
