import asyncio
import discord
from discord.ext import commands

intents = discord.Intents().all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Bot is ready.')

roles = {
    'Bronze': ['Bronze 1', 'Bronze 2', 'Bronze 3'],
    'Silver': ['Silver 1', 'Silver 2'],
    'Gold': ['Gold 1', 'Gold 2'],
    'Platinum': ['Platinum 1', 'Platinum 2'],
    'Diamond': ['Diamond 1', 'Diamond 2'],
    'Crimson': ['Crimson 1', 'Crimson 2'],
    'IRIDESCENT': ['IRIDESCENT 1', 'IRIDESCENT 2'],
    'TOP 250': ['TOP 250 1', 'TOP 250 2']
}

@bot.command()
async def rank(ctx):
    embed = discord.Embed(title="Available Roles", color=discord.Color.gold())

    for tier, tier_roles in roles.items():
        formatted_roles = '\n'.join([f'{role}' for role in tier_roles])
        embed.add_field(name=tier, value=formatted_roles, inline=False)

    embed.set_footer(text="To choose a role, type !choose <role_name>")
    await ctx.send(embed=embed)

@bot.command()
async def choose(ctx, *, role_name: str):
    all_roles = [role for roles_list in roles.values() for role in roles_list]

    if role_name in all_roles:
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if role:
            await ctx.author.add_roles(role)
            await ctx.send(f'{ctx.author.mention} has been assigned the {role_name} role.')
        else:
            await ctx.send("Role not found.")
    else:
        await ctx.send("Invalid role name. Please choose from the available roles.")

bot.run('')
