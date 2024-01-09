import discord, requests
from discord.ext import commands
from config import *

intents = discord.Intents.default()
intents.all()
bot = commands.Bot(command_prefix=prefix, intents=intents)

def exist(username):
    # vérifie si l'utilisateur existe
    url = "https://tryhackme.com/api/similar-users/" + username
    return '"'+username+'"' in requests.get(url).text

@bot.event
async def on_ready():
    print(f'Bip boop boop\nConnected: {bot.user.name} ({bot.user.id})')

@bot.command(name='add-user')
async def add_user(ctx, username):
    # ajoute username au fichier users.txt
    if not exist(username):
        await ctx.send(f'L\'utilisateur {username} n\'existe pas.')
        return
    users = open("users.txt", "r").readlines()
    for line in users:
        if line.strip("\n") == username:
            await ctx.send(f'L\'utilisateur {username} est déjà dans la liste.')
            return
    f = open("users.txt", "a")
    f.write(username + "\n")
    f.close()
    await ctx.send(f'L\'utilisateur {username} a été ajouté.')

@bot.command(name='remove-user')
async def remove_user(ctx, username):
    # retire username du fichier users.txt
    users = open("users.txt", "r").readlines()
    f = open("users.txt", "w")
    for line in users:
        if line.strip("\n") != username:
            f.write(line)
    f.close()
    await ctx.send(f'L\'utilisateur {username} a été supprimé.')

@bot.command(name='leaderboard')
async def display_leaderboard(ctx):
    # todo
    return
@bot.command(name='user-info')
async def display_leaderboard(ctx, username):
    # todo
    if not exist(username):
        await ctx.send(f'L\'utilisateur {username} n\'existe pas.')
        return
    # todo 
    # api doc : https://documenter.getpostman.com/view/18269560/UVCB9j5e#5c827973-cc77-4db5-8e6b-201252c5c5b2
    return
bot.run(token)
