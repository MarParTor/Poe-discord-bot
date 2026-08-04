import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import poem_scraper
import webserver

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.reply('pong')

@bot.command()
async def poe(ctx):
    poem = poem_scraper.get_poem()
    while len(poem) > 2000: # discord no acepta mensjes de más de 2000 caracteres
        poem = poem_scraper.get_poem()
    mensaje = await ctx.reply(poem)
    await mensaje.add_reaction('⬆️')
    await mensaje.add_reaction('⬇️')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')

webserver.keep_alive()
bot.run(os.getenv('BOT_TOKEN'))

