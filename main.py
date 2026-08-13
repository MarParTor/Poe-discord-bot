import os
import discord
from discord.ext import commands, tasks 
from bs4 import BeautifulSoup
import poem_scraper
import webserver

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

defaultChannel = None

async def send_poem(context, reply = False):
    poem = poem_scraper.get_poem()
    while len(poem) > 2000: # discord no acepta mensjes de más de 2000 caracteres
        poem = poem_scraper.get_poem()
    if reply:
        mensaje = await context.reply(poem)
    else:
        mensaje = await context.send(poem)
    await mensaje.add_reaction('⬆️')
    await mensaje.add_reaction('⬇️')


@bot.command()
async def help(ctx):
    help_message = (
        "```Comandos disponibles:\n"
        "$poe - Envía un poema aleatorio.\n"
        "\n --Automatización-- (solo para administración) \n\n"
        "$changePoemInterval <minutos> - Cambia el intervalo de envío automático de poemas (mínimo 1 minuto).\n"
        "- 24h -> 1440 minutos.\n"
        "- 7 dias -> 10080 minutos.\n"
        "$setDefaultChannel - Establece el canal predeterminado para enviar poemas automáticamente.\n"
        "$startScheduledPoe - Inicia el envío automático de poemas y establece ese canal como predeterminado.\n"
        "$stopScheduledPoe - Detiene el envío automático de poemas.```\n"
    )
    await ctx.reply(help_message)

@bot.command(help="Envía un poema aleatorio.")
async def poe(ctx):
    await send_poem(ctx, reply=True)

@bot.command(help="Cambia el intervalo de envío automático de poemas (mínimo 1 minuto).")
@commands.has_permissions(administrator=True)
async def changePoemInterval(ctx, timeMinutes: float):
    if timeMinutes < 1:
        await ctx.reply('El intervalo mínimo permitido es de 1 minuto.')
        timeMinutes = 1
    sendScheduledPoem.change_interval(minute=timeMinutes)
    await ctx.reply(f'Intervalo de envío de poemas establecido a {timeMinutes} minutos.')


@bot.command(help="Establece el canal predeterminado para enviar poemas automáticamente.")
@commands.has_permissions(administrator=True)
async def setDefaultChannel(ctx):
    global defaultChannel
    defaultChannel = ctx.channel
    await ctx.reply(f'Canal predeterminado establecido a {defaultChannel.name}.')

@bot.command(help="Inicia el envío automático de poemas y establece ese canal como predeterminado.")
@commands.has_permissions(administrator=True)
async def startScheduledPoe(ctx):
    await ctx.reply('Envío automático iniciado.')
    global defaultChannel
    defaultChannel = ctx.channel
    sendScheduledPoem.start()

@bot.command(help="Detiene el envío automático de poemas.")
@commands.has_permissions(administrator=True)
async def stopScheduledPoe(ctx):
    sendScheduledPoem.stop()
    await ctx.reply('Envío automático detenido.')

@tasks.loop(minutes=1)
async def sendScheduledPoem():
    if defaultChannel:
        await send_poem(defaultChannel, reply=False)

@bot.event
async def on_command_error(ctx, error):

    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            "¡Ey! no tienes permisos para utilizar este comando ;("
        )

@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')

webserver.keep_alive()
bot.run(os.getenv('BOT_TOKEN'))


