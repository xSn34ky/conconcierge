import discord
import asyncio
from discord.ext import commands

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

@bot.event
async def on_ready():
    print('Concierge is ready.')

@bot.command()
async def rank(ctx):
    roles = ['BRONZE', 'SILVER', 'GOLD', 'PLATIMUN', 'DIAMOND', 'CRIMSON', 'IRIDESCENT', 'TOP250']  # List of roles to display
    formatted_roles = '\n'.join([f'{index + 1}. {role}' for index, role in enumerate(roles)])
    
    embed = discord.Embed(title="Rank Roles", description=formatted_roles, color=discord.Color.gold())
    embed.set_footer(text="React with the emoji corresponding to the role you want.")

    message = await ctx.send(embed=embed)

    reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']  # Emoji reactions corresponding to each role

    for reaction in reactions[:len(roles)]:
        await message.add_reaction(reaction)

    while True:
        try:
            reaction, user = await bot.wait_for('reaction_add', timeout=60)

            if user.bot:
                continue

            role_index = reactions.index(str(reaction.emoji))
            chosen_role = roles[role_index]

            role = discord.utils.get(ctx.guild.roles, name=chosen_role)
            if role:
                # Remove the chosen role if the user already has it
                for user_role in user.roles:
                    if user_role.name in roles:
                        await user.remove_roles(user_role)
                        break
                
                # Assign the new role to the user
                await user.add_roles(role)
                await ctx.send(f'{user.mention} has been assigned the {role.name} role.')
            else:
                await ctx.send("Role not found.")
        except asyncio.TimeoutError:
            break
        except ValueError:
            continue

bot.run('')
