import os
import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import poem_scraper

port = os.getenv('PORT') # render stuff

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.reply('pong')

@bot.command()
async def poe(ctx):
    p = poem_scraper.get_poem()
    while p.len(p) > 4000: # discord no acepta mensjes de más de 4000 caracteres
        p = poem_scraper.get_poem()
    mensaje = await ctx.reply(p)
    await mensaje.add_reaction('⬆️')
    await mensaje.add_reaction('⬇️')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')


bot.run(os.getenv('BOT_TOKEN'))

