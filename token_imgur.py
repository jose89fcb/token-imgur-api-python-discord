import os
import discord
from discord.ext import commands
from discord_slash import SlashCommand
from discord_slash.model import SlashCommandOptionType
from dotenv import load_dotenv
import json
import requests

load_dotenv()

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
slash = SlashCommand(bot, sync_commands=True)

# Ruta al directorio de archivos de configuración
CONFIG_DIR = "ARCHIVO DE CONFIGURACION"
CONFIG_FILE = os.path.join(CONFIG_DIR, "config.json")

# Crear el directorio si no existe
os.makedirs(CONFIG_DIR, exist_ok=True)

# Variables globales para almacenar el Client-ID y el código de autorización
imgur_client_id = os.getenv("IMGUR_CLIENT_ID", "")
imgur_client_secret = os.getenv("IMGUR_CLIENT_SECRET", "")
authorization_code = ""

# Define el comando slash para establecer las claves de Imgur
@slash.slash(
    name="set_imgur_keys",
    description="Establece las claves de Imgur",
    options=[
        {
            "name": "client_id",
            "description": "Client ID de Imgur",
            "type": SlashCommandOptionType.STRING,
            "required": True
        },
        {
            "name": "client_secret",
            "description": "Client Secret de Imgur",
            "type": SlashCommandOptionType.STRING,
            "required": True
        }
    ]
)
async def set_imgur_keys(ctx, client_id, client_secret):
    global imgur_client_id, imgur_client_secret
    imgur_client_id = client_id
    imgur_client_secret = client_secret

    # Actualiza el archivo de configuración
    update_config()

    embed = discord.Embed(title="Claves de Imgur establecidas correctamente", color=0x00ff00)
    await ctx.send(embed=embed, hidden=True)

# Define el comando slash para obtener la URL de autorización
@slash.slash(
    name="get_authorization_url",
    description="Obtiene la URL de autorización de Imgur"
)
async def get_authorization_url(ctx):
    global imgur_client_id
    # Verifica que el Client ID esté establecido
    if not imgur_client_id:
        embed = discord.Embed(title="Error", description="Por favor, establece el Client ID usando el comando `/set_imgur_keys` antes de obtener la URL de autorización.", color=0xff0000)
        await ctx.send(embed=embed, hidden=True)
        return

    # Construye la URL de autorización
    authorization_url = f'https://api.imgur.com/oauth2/authorize?client_id={imgur_client_id}&response_type=code'
    embed = discord.Embed(title="URL de autorización de Imgur", description=f"[Haz clic aquí para autorizar la aplicación]({authorization_url})", color=0x00ff00)
    await ctx.send(embed=embed, hidden=True)

# Define el comando slash para intercambiar el código por un token de acceso
@slash.slash(
    name="exchange_code_for_token",
    description="Intercambia el código de autorización por un token de acceso",
    options=[
        {
            "name": "authorization_code",
            "description": "Código de autorización obtenido de Imgur",
            "type": SlashCommandOptionType.STRING,
            "required": True
        }
    ]
)
async def exchange_code_for_token(ctx, authorization_code):
    global imgur_client_id, imgur_client_secret
    # Verifica que el Client ID esté establecido
    if not imgur_client_id:
        embed = discord.Embed(title="Error", description="Por favor, establece el Client ID usando el comando `/set_imgur_keys` antes de intercambiar el código por un token.", color=0xff0000)
        await ctx.send(embed=embed, hidden=True)
        return

    # Intercambia el código por un token de acceso
    data = {
        'client_id': imgur_client_id,
        'client_secret': imgur_client_secret,
        'grant_type': 'authorization_code',
        'code': authorization_code
    }

    response = requests.post('https://api.imgur.com/oauth2/token', data=data)
    result = response.json()

    if 'access_token' in result:
        access_token = result['access_token']
        embed = discord.Embed(title="Access Token", description=f"El Access Token es: {access_token}", color=0x00ff00)
        await ctx.send(embed=embed, hidden=True)
    else:
        embed = discord.Embed(title="Error", description=f"Error al obtener el Access Token: {result}", color=0xff0000)
        await ctx.send(embed=embed, hidden=True)

# ...

# Actualiza el archivo de configuración JSON
def update_config():
    global imgur_client_id, imgur_client_secret

    # Crear el directorio si no existe
    os.makedirs(CONFIG_DIR, exist_ok=True)

    # Crear o cargar el archivo de configuración
    if not os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'w') as f:
            f.write('{}')

    # Leer el archivo de configuración
    with open(CONFIG_FILE, 'r') as f:
        config_data = json.load(f)

    # Actualizar las claves de Imgur
    config_data['imgur'] = {
        'client_id': imgur_client_id,
        'client_secret': imgur_client_secret
    }

    # Escribir las actualizaciones en el archivo
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config_data, f, indent=2)

# ...

# Ejecuta el bot con el token de Discord
bot.run(os.getenv("DISCORD_TOKEN", ""))
