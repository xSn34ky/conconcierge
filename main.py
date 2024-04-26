import discord
from discord.ext import commands
from PIL import Image, ImageDraw, ImageFont, ImageOps
from io import BytesIO
import asyncio

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
        avatar_bytes = await member.avatar_url.read()
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
        text_width, text_height = draw.textsize(f"Welcome, {member.name}!", font=font)
        image_width, image_height = base_image.size
        text_position = ((image_width - text_width) / 2, (image_height - text_height) / 2)
        
        # Draw member's name
        draw.text(text_position, f"Welcome, {member.name}!", fill="white", font=font)
        
        # Paste avatar on the base image
        base_image.paste(avatar_image, (0, int((image_height - avatar_size[1]) / 2)), avatar_image)  # Align avatar to the left
        
        # Save the edited image to a BytesIO object
        image_io = BytesIO()
        base_image.save(image_io, format='PNG')
        image_io.seek(0)
        
        # Send the modified image as a welcome message to the specified channel
        await welcome_channel.send(f"Welcome to the server, {member.mention}!", file=discord.File(image_io, filename='welcome.png'))
    else:
        print("Welcome channel not found.")

@bot.event
async def on_member_join(member):
    print(f"{member.name} joined the server.")
    await send_welcome_message(member)

@bot.event
async def on_member_update(before, after):
    # Check if the member has joined the server by comparing role changes
    if len(before.roles) < len(after.roles):
        print(f"{after.name} rejoined the server.")
        await send_welcome_message(after)

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
