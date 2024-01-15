import functools
import typing

import discord
from discord.ext import commands
import aiohttp

from config import DISCORD_BOT_TOKEN, COMMAND_PREFIX, USER_LIST_FILE_NAME

"""
TODO:
---
    - [ ] Afficher la liste des commandes
    - [ ] new-rooms: fonctionnel
    - [ ] add-user : fonctionnel
    - [ ] remove-user: fonctionnel
    - [ ] user-info: fonctionnel
"""

class TryHackMeUser(typing.TypedDict):
    userId: str
    username: str
    avatar: str


class UserList:
    """La liste des utilisateurs trackés par le bot, avec des méthodes pour
    synchroniser les données sur le disque au besoin.
    """
    users: set[str]
    filepath: str

    def __init__(self, filepath: str) -> None:
        self.users = set()
        self.filepath = filepath
        try:
            with open(self.filepath, "r") as file:
                self.users.update(file.read().splitlines())
        except FileNotFoundError:
            open(self.filepath, "w").close()

    def sync_to_disk(self):
        """Synchronise la liste des utilisateurs sur le disque.
        """
        with open(self.filepath, "w") as file:
            for user in self.users:
                file.write(f"{user}\n")



bot = commands.Bot(command_prefix=COMMAND_PREFIX, intents=discord.Intents.all())
user_list = UserList(USER_LIST_FILE_NAME)


@functools.lru_cache
async def get_tryhackme_user(username: str) -> TryHackMeUser | None:
    """Renvoie si un utilsateur existe parmis les utilisateurs de TryHackMe.

    Args:
        username (str): Le pseudo de l'utilisateur.

    Returns:
        bool: True si l'utilisateur existe, False sinon.
    """
    url = f"https://tryhackme.com/api/user/exist/{username}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return (await response.json()).get("success")

    return None


@bot.event
async def on_ready():
    if bot.user:
        print(f"Bip boop boop\nConnected: {bot.user.name} ({bot.user.id})")
    else:
        print("Impossible de récupérer l'utilisateur associé au compte du bot Discord.")
        exit(1)


@bot.command(name="add-user")
async def add_user_command(ctx: commands.Context, username: str):
    """Ajoute un utilisateur à la liste.

    Args:
        ctx (commands.Context): La context.
        username (str): Le pseudo de l'utilisateur.
    """
    if username in user_list.users:
        await ctx.send(f"L'utilisateur {username} est déjà dans la liste.")
        return

    # Fait un appel à la base de données de tryhackme, peut prend du temps.
    async with ctx.typing():
        if not await get_tryhackme_user(username):
            await ctx.send(f"Aucun utilisateur trouvé pour le pseudo `{username}`.")
            return
        user_list.users.add(username)
        user_list.sync_to_disk()

        await ctx.send(
            embed=discord.Embed(
                title="Utilisateur ajouté !",
                description=f"L'Utilisateur {user['username']} (`{user['userId']}`) a été ajouté.",  # noqa
            ).set_thumbnail(
                url=user["avatar"]
            )
        )


@bot.command(name="remove-user")
async def remove_user_command(ctx: commands.Context, username: str):
    """Retire un utilisateur de la liste.

    Args:
        ctx (commands.Context): Le contexte d'execution.
        username (str): Le pseudo de l'utilisateur.
    """
    user_list.users.remove(username)
    user_list.sync_to_disk()
    await ctx.send(f"L'utilisateur {username} a été supprimé.")

@bot.command(name="user-list")
async def user_list_command(ctx: commands.Context):
    """Renvoie la liste des utilisateurs trackés par le bot.

    Args:
        ctx (commands.Context): Le contexte d'execution.
    """
    if user_list.users:
        await ctx.send(
            "Liste des utilisateurs trackés par le bot:"
            + "```"
            + "\n"
            + "\n".join(user_list.users)
            + "```"
        )
    else:
        await ctx.send("Aucune utilisateur tracké par le bot !")


@bot.command(name="leaderboard")
async def leaderboard_command(ctx):
    # todo

    return


@bot.command(name="user-info")
async def user_info_command(ctx, username):
    # todo
    if not get_tryhackme_user(username):
        await ctx.send(f"L'utilisateur {username} n'existe pas.")
        return
    # todo
    # api doc : https://documenter.getpostman.com/view/18269560/UVCB9j5e#5c827973-cc77-4db5-8e6b-201252c5c5b2
    return

@bot.command(name="new-rooms")
async def new_rooms_command(ctx):
    async with ctx.typing():
        async with aiohttp.ClientSession() as session:
            async with session.get("https://tryhackme.com/api/new-rooms") as response:
                rooms = await response.json()
                
                embed = discord.Embed(
                    title="Nouvelles rooms:"
                    )
                
                for room in rooms:
                    emoji = ":office_worker:" if room["type"] == "walkthrough" else ":triangular_flag_on_post:"
                    name = room["title"]
                    desc = room["description"]
                    img = room["imageURL"]
                    creator = room["creator"]
                    url = "https://tryhackme.com/room/" + room["code"]

                    room_embed = discord.Embed(
                        type="rich",
                        title=emoji + name,
                        description="",
                        color=0xbf0e0e
                    )
                    
                    room_embed.add_field(
                        name="Auteur: " + creator,
                        value="\u200B"
                    )
                    
                    room_embed.set_image(
                        url=img
                    )

                    embed.add_field(room_embed)

                await ctx.send(embed=embed)


bot.run(DISCORD_BOT_TOKEN)
