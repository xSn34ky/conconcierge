import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import asyncio
import json

intents = discord.Intents.all()
intents.members = True

bot = commands.Bot(command_prefix='!', intents=intents)

welcome_channel_id = '1232359152395747400'

# Set the dimensions for the user's picture and text
avatar_size = (500, 500)  # Size of the user's picture
font_size = 70  # Font size for the text

@bot.event
async def on_ready():
    print('Concierge is ready.')

async def send_welcome_message(member):
    welcome_channel = bot.get_channel(int(welcome_channel_id))
    if welcome_channel:
        # Open the base image
        base_image = Image.open('Welcome.png')  # Replace with your image path

        # Get member's avatar (profile picture)
        avatar_bytes = await member.avatar.read()
        avatar_image = Image.open(BytesIO(avatar_bytes))
        avatar_image = avatar_image.resize(avatar_size)  # Resize the avatar

        # Create circular mask
        mask = Image.new("L", avatar_size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + avatar_size, fill=255)

        # Apply mask to avatar image
        avatar_image = ImageOps.fit(avatar_image, mask.size, centering=(0.5, 0.5))
        avatar_image.putalpha(mask)

        # Load a font
        font = ImageFont.truetype("ArialCEMTBlack.ttf", font_size)

        # Create a drawing context
        draw = ImageDraw.Draw(base_image)

        # Calculate the position to center the text vertically
        text_bbox = draw.textbbox((0, 0), f"Welcome, {member.name}!", font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_height = text_bbox[3] - text_bbox[1]
        image_width, image_height = base_image.size
        text_position = ((image_width - text_width) / 2, (image_height - text_height) / 2)

        # Draw member's name
        draw.text(text_position, f"Welcome, {member.name}!", fill="white", font=font)

        # Paste avatar on the base image
        base_image.paste(avatar_image, (0, int((image_height - avatar_size[1]) / 2)), avatar_image)  # Align                                                                                                                                  avatar to the left

        # Save the edited image to a BytesIO object
        image_io = BytesIO()
        base_image.save(image_io, format='PNG')
        image_io.seek(0)

        # Send the modified image as a welcome message to the specified channel
        await welcome_channel.send(f"Welcome to the server, {member.mention}!", file=discord.File(image_io,                                                                                                                                  filename='welcome.png'))
    else:
        print("Welcome channel not found.")

@bot.event
async def on_member_join(member):
    print(f"{member.name} joined the server.")
    await send_welcome_message(member)

#@bot.event
#async def on_member_update(before, after):
     #Check if the member has joined the server by comparing role changes
     #if len(before.roles) < len(after.roles):
        #print(f"{after.name} rejoined the server.")
        #await send_welcome_message(after)

roles = ['BRONZE', 'SILVER', 'GOLD', 'PLATINUM', 'DIAMOND', 'CRIMSON', 'IRIDESCENT', 'TOP250']  # List of roles to display
reactions = ['1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣', '6️⃣', '7️⃣', '8️⃣']  # Emoji reactions corresponding to each role

@bot.command()
async def rank(ctx):
    formatted_roles = '\n'.join([f'{index + 1}. {role}' for index, role in enumerate(roles)])

    embed = discord.Embed(title="Rank Roles", description=formatted_roles, color=discord.Color.gold())
    embed.set_footer(text="React with the emoji corresponding to the role you want.")

    message = await ctx.send(embed=embed)

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
                        await ctx.send(f'{user.mention} has been removed from the {user_role.name} role.')

                # Assign the new role to the user
                await user.add_roles(role)
                await ctx.send(f'{user.mention} has been assigned the {role.name} role.')
            else:
                await ctx.send("Role not found.")
        except asyncio.TimeoutError:
            break

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    role_index = reactions.index(str(reaction.emoji))
    chosen_role = roles[role_index]

    role = discord.utils.get(user.guild.roles, name=chosen_role)
    if role:
        await user.remove_roles(role)
        await reaction.message.channel.send(f"{user.mention} has been removed from the {role.name} role because they removed their reaction.")

        # Now, let's check if the user still has a reaction for any other role and assign it if so
        for user_reaction in reaction.message.reactions:
            if user_reaction.emoji == reaction.emoji:
                continue  # Skip the removed reaction
            async for reaction_user in user_reaction.users():
                if reaction_user == user:
                    await reaction.message.channel.send(f"{user.mention} re-added the reaction, assigning the corresponding role...")
                    await user.add_roles(discord.utils.get(user.guild.roles, name=roles[reactions.index(str(user_reaction.emoji))]))
                    await reaction.message.channel.send(f"{user.mention} has been assigned the {roles[reactions.index(str(user_reaction.emoji))]} role.")
                    break  # Exit loop after assigning role

@bot.event
async def on_reaction_remove(reaction, user):
    if user.bot:
        return

    role_index = reactions.index(str(reaction.emoji))
    chosen_role = roles[role_index]

    role = discord.utils.get(user.guild.roles, name=chosen_role)
    if role:
        await user.remove_roles(role)
        await reaction.message.channel.send(f"{user.mention} has been removed from the {role.name}")

# Dictionary to store gamertags
gamertags = {}

specified_channel_id = "1232652899251650611"


specified_category_id = "1232763700482408538"

@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def voice(ctx):
    if ctx.author.voice is None or ctx.author.voice.channel is None:
        await ctx.send("You are not in a voice channel!")
        return

    voice_channel = ctx.author.voice.channel
    guild = ctx.guild

    # Get the specified category
    category = discord.utils.get(guild.categories, id=int(specified_category_id))

    if category is None:
        await ctx.send("Failed to find the specified category.")
        return

    # Create a new private voice channel under the specified category
    new_channel = await guild.create_voice_channel(name="Temporary Voice Channel", category=category, user_limit=1)

    # Move users in the same voice channel to the new channel
    for member in voice_channel.members:
        await member.move_to(new_channel)

    await ctx.send("Moved users to temporary voice channel.")

@bot.event
async def on_voice_state_update(member, before, after):
    if before.channel is not None and before.channel.name.startswith("Temporary Voice Channel") and len(before.channel.members) == 0:
        # Delete empty temporary voice channels
        await before.channel.delete()


# Dictionary to store gamertags
gamertags = {}

# Load gamertags from file
def load_gamertags():
    global gamertags
    try:
        with open('gamertags.json', 'r') as f:
            gamertags = json.load(f)
    except FileNotFoundError:
        print("Gamertags file not found. Starting with empty dictionary.")
        gamertags = {}
    except json.decoder.JSONDecodeError:
        print("Error decoding JSON. Starting with empty dictionary.")
        gamertags = {}
    except Exception as e:
        print(f"Error loading gamertags: {e}")
        gamertags = {}


# Save gamertags to file
def save_gamertags():
    try:
        with open('gamertags.json', 'w') as f:
            json.dump(gamertags, f)
    except Exception as e:
        print(f"Error saving gamertags: {e}")

# Event listener for bot's on_ready event
@bot.event
async def on_ready():
    print(f'{bot.user.name} has connected to Discord!')
    load_gamertags()
    print("Gamertags loaded:", gamertags)


# Command to create gamertag
@bot.command()
async def create(ctx, gamertag):
    user = ctx.author
    gamertags[user.id] = gamertag
    save_gamertags()
    load_gamertags()
    await ctx.send(f'Gamertag `{gamertag}` added for {user.mention}')

@bot.command()
async def team(ctx):
    # Check if the command was executed in the specified channel
    if str(ctx.channel.id) != specified_channel_id:
        await ctx.send("This command can only be used in cod-namecode channel.")
        return
    
    user = ctx.author
    if ctx.author.voice is None:
        await ctx.send("You're not in a voice channel.")
        return
    
    voice_channel = ctx.author.voice.channel
    users_in_channel = {str(member.id) for member in voice_channel.members}  # Convert IDs to strings
    
    print("Users in channel:", users_in_channel)
    print("All gamertags:", gamertags)
    
    gamertags_in_channel = {}
    for user_id in users_in_channel:
        if user_id in gamertags:
            gamertags_in_channel[user_id] = gamertags[user_id]
        else:
            print(f"No gamertag found for user ID {user_id}")
    
    print("Gamertags in channel:", gamertags_in_channel)
    print("User ID:", user.id)
    
    gamertags_message = ""
    for user_id, gamertag in gamertags_in_channel.items():
        member = ctx.guild.get_member(int(user_id))  # Convert user ID back to integer
        if member:
            gamertags_message += f"{member.display_name}: {gamertag}\n"
    
    if gamertags_message:
        await ctx.send(f'Team {user.mention}:\n{gamertags_message}')
    else:
        await ctx.send('No gamertags found for users in the voice channel.')

bot.run('')
