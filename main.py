import os
import discord
from discord.ext import commands, tasks
from bs4 import BeautifulSoup
import poem_scraper
import webserver

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents, help_command=None)

# Almacena la configuración de cada servidor por separado.
# guild_data[guild_id] = {'channel': discord.TextChannel, 'task': tasks.Loop}
guild_data = {}


async def send_poem(context, reply=False):
    poem = poem_scraper.get_poem()
    while len(poem) > 2000:  # discord no acepta mensajes de más de 2000 caracteres
        poem = poem_scraper.get_poem()
    if reply:
        mensaje = await context.reply(poem)
    else:
        mensaje = await context.send(poem)
    await mensaje.add_reaction('⬆️')
    await mensaje.add_reaction('⬇️')


def get_guild_entry(guild_id):
    """Crea (si no existe) y devuelve la entrada de configuración de un servidor."""
    if guild_id not in guild_data:
        guild_data[guild_id] = {'channel': None, 'task': None}
    return guild_data[guild_id]


def create_guild_task(guild_id):
    """Crea una tarea (tasks.Loop) independiente para el servidor indicado."""

    @tasks.loop(minutes=1)
    async def scheduled_poem_task():
        entry = guild_data.get(guild_id)
        if entry and entry.get('channel'):
            await send_poem(entry['channel'], reply=False)

    return scheduled_poem_task


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
@commands.guild_only()
async def changePoemInterval(ctx, timeMinutes: float):
    if timeMinutes < 1:
        await ctx.reply('El intervalo mínimo permitido es de 1 minuto.')
        timeMinutes = 1

    entry = get_guild_entry(ctx.guild.id)

    if entry['task'] is None:
        entry['task'] = create_guild_task(ctx.guild.id)

    entry['task'].change_interval(minutes=timeMinutes)
    await ctx.reply(f'Intervalo de envío de poemas establecido a {timeMinutes} minutos.')


@bot.command(help="Establece el canal predeterminado para enviar poemas automáticamente.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def setDefaultChannel(ctx):
    entry = get_guild_entry(ctx.guild.id)
    entry['channel'] = ctx.channel
    await ctx.reply(f'Canal predeterminado establecido a {entry["channel"].name}.')


@bot.command(help="Inicia el envío automático de poemas y establece ese canal como predeterminado.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def startScheduledPoe(ctx):
    entry = get_guild_entry(ctx.guild.id)
    entry['channel'] = ctx.channel

    if entry['task'] is None:
        entry['task'] = create_guild_task(ctx.guild.id)

    if entry['task'].is_running():
        await ctx.reply('El envío automático ya estaba iniciado en este servidor.')
    else:
        entry['task'].start()
        await ctx.reply('Envío automático iniciado.')


@bot.command(help="Detiene el envío automático de poemas.")
@commands.has_permissions(administrator=True)
@commands.guild_only()
async def stopScheduledPoe(ctx):
    entry = guild_data.get(ctx.guild.id)
    if entry and entry['task'] and entry['task'].is_running():
        entry['task'].stop()
        await ctx.reply('Envío automático detenido.')
    else:
        await ctx.reply('El envío automático no estaba activo.')


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.reply(
            "¡Ey! no tienes permisos para utilizar este comando ;("
        )
    elif isinstance(error, commands.NoPrivateMessage):
        await ctx.reply(
            "Este comando solo se puede usar dentro de un servidor ;("
        )


@bot.event
async def on_ready():
    print(f'Bot conectado como {bot.user.name} (ID: {bot.user.id})')


webserver.keep_alive()
import bot_secrets
bot.run(bot_secrets.BOT_TOKEN)
#bot.run(os.getenv('BOT_TOKEN'))
