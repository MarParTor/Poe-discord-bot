import discord
from discord.ext import commands
from bs4 import BeautifulSoup
import bot_secrets
import poem_scraper

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

@bot.command()
async def ping(ctx):
    await ctx.reply('pong')

@bot.command()
async def poe(ctx):
    p = poem_scraper.get_poem()
    mensaje = await ctx.reply(p)
    await mensaje.add_reaction('⬆️')
    await mensaje.add_reaction('⬇️')

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')


bot.run(bot_secrets.BOT_TOKEN)

