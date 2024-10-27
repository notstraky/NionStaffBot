import discord
from discord.ext import commands
from discord import app_commands
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

# Crear una instancia del bot
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix=",", intents=intents)

# Canal predeterminado para recibir sugerencias
SUGGESTION_CHANNEL_ID = 1299971376085598229  # ID del canal de revisión de sugerencias
NOTIFICATION_CHANNEL_ID = 1299884865142919208  # ID del canal de anuncios

# Evento cuando el bot esté listo
@bot.event
async def on_ready():
    print(f'Bot {bot.user} se ha conectado a Discord')
    
    # Cambiar estado a 'Jugando a Nion Staff'
    await bot.change_presence(activity=discord.Game(name="Nion Staff"))

    # Sincronizar los comandos slash
    await bot.tree.sync()

# Comando para enviar sugerencias con prefijo
@bot.command(name='sugerencia')
async def sugerencia(ctx, *, mensaje: str):
    suggestion_channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if suggestion_channel:
        embed = discord.Embed(
            title="Nueva sugerencia",
            description=f"{ctx.author} dice: {mensaje}",
            color=discord.Color.blue()
        )
        await suggestion_channel.send(embed=embed)
        await ctx.send("Gracias por tu sugerencia, la hemos recibido.")

# Comando slash para sugerencias (disponible para todos)
@bot.tree.command(name="sugerencia", description="Envía una sugerencia")
async def slash_sugerencia(interaction: discord.Interaction, mensaje: str):
    suggestion_channel = bot.get_channel(SUGGESTION_CHANNEL_ID)
    if suggestion_channel:
        embed = discord.Embed(
            title="Nueva sugerencia",
            description=f"{interaction.user} dice: {mensaje}",
            color=discord.Color.blue()
        )
        await suggestion_channel.send(embed=embed)
        await interaction.response.send_message("Gracias por tu sugerencia, la hemos recibido.", ephemeral=True)

# Restricción para comandos de "embed" y "notificar" (solo roles específicos)
def check_roles(roles_permitidos):
    async def predicate(interaction: discord.Interaction):
        user_roles = [role.id for role in interaction.user.roles]
        return any(role_id in user_roles for role_id in roles_permitidos)
    return app_commands.check(predicate)

# ID de los roles permitidos
ROLES_PERMITIDOS = [1299953473604816906, 1299952826880884847, 1299882709501476864, 1299952907936075797]  # Cambia estos IDs a los de tus roles específicos

# Comando slash para enviar notificaciones (solo roles específicos)
@bot.tree.command(name="notificar", description="Envía una notificación a un canal específico")
@check_roles(ROLES_PERMITIDOS)
async def notificar(interaction: discord.Interaction, mensaje: str):
    notification_channel = bot.get_channel(NOTIFICATION_CHANNEL_ID)
    if notification_channel:
        await notification_channel.send(f"Notificación: {mensaje}")
        await interaction.response.send_message(f"Notificación enviada al canal {notification_channel.mention}", ephemeral=True)

@notificar.error
async def notificar_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("No tienes permiso para usar este comando.", ephemeral=True)

# Comando slash para crear y enviar un embed (solo roles específicos)
@bot.tree.command(name="embed", description="Crea y envía un mensaje embebido")
@app_commands.describe(canal="Elige el canal donde enviar el embed", titulo="Título del embed", mensaje="Mensaje del embed", footer="Pie de página del embed (opcional)")
@check_roles(ROLES_PERMITIDOS)
async def crear_embed(interaction: discord.Interaction, canal: discord.TextChannel, titulo: str, mensaje: str, footer: str = None):
    embed = discord.Embed(title=titulo, description=mensaje, color=discord.Color.green())

    # Agregar el pie de página si se proporciona
    if footer:
        embed.set_footer(text=footer)

    # Enviar el embed al canal especificado
    await canal.send(embed=embed)
    await interaction.response.send_message(f"Embed enviado al canal {canal.mention}", ephemeral=True)

@crear_embed.error
async def crear_embed_error(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.CheckFailure):
        await interaction.response.send_message("No tienes permiso para usar este comando.", ephemeral=True)

# Comando slash para mostrar ayuda
@bot.tree.command(name="help", description="Muestra una lista de todos los comandos disponibles")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(title="Comandos del Bot", color=discord.Color.blue())
    embed.add_field(name="/sugerencia", value="Envía una sugerencia anónima al canal de sugerencias.", inline=False)
    embed.add_field(name="/notificar", value="Envía una notificación a un canal (Solo para roles permitidos).", inline=False)
    embed.add_field(name="/embed", value="Crea y envía un mensaje embebido en un canal específico (Solo para roles permitidos).", inline=False)
    embed.add_field(name=",sugerencia", value="Envía una sugerencia usando el prefijo de comando (disponible para todos).", inline=False)
    
    await interaction.response.send_message(embed=embed, ephemeral=True)

# Iniciar el bot
bot.run(TOKEN)
