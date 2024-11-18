import discord
from discord.ext import commands
from dotenv import load_dotenv
import os

load_dotenv()
secret_key = os.getenv("SECRET_KEY")

# Initialize the bot
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)

# Event triggered when a member joins the server
@bot.event
async def on_member_join(member):
    guild = member.guild  # Get the server (guild) the member joined

    # Find the category named 'Requests'
    category = discord.utils.get(guild.categories, name="Requests")
    if category is None:
        # If the category does not exist, create it
        category = await guild.create_category(name="Requests")

    # Set up permissions for the channel
    bot_member = guild.me  # Get the bot's member instance
    overwrites = {
        guild.default_role: discord.PermissionOverwrite(read_messages=False),  # Default role can't see the channel
        member: discord.PermissionOverwrite(read_messages=True),  # The member can see the channel
        bot_member: discord.PermissionOverwrite(read_messages=True, send_messages=True),  # Bot can access the channel
    }

    # Grant CEO role access
    ceo_role = discord.utils.get(guild.roles, name="CEO")
    if ceo_role:
        overwrites[ceo_role] = discord.PermissionOverwrite(read_messages=True)

    # Create the channel under the category
    channel = await guild.create_text_channel(
        name=f"welcome-{member.name}",
        overwrites=overwrites,
        category=category,  # Specify the category
        reason="New member private channel under Requests",
    )

    # Send a welcome message in the private channel
    await channel.send(f"Welcome to the server, {member.mention}! This channel is private to you, the CEOs, and the bot.")

@bot.command(name="close")
async def close_channel(ctx):
    """Deletes the channel if it's under the Requests category and user is a CEO. Also kicks all members without the CEO role."""
    # Get the channel and its category
    channel = ctx.channel
    category = channel.category

    # Ensure the channel is under the 'Requests' category
    if category and category.name == "Requests":
        # Check if the user has the CEO role
        ceo_role = discord.utils.get(ctx.guild.roles, name="CEO")
        if ceo_role in ctx.author.roles:
            await ctx.send("Closing the channel and kicking unauthorized members...")

            # Kick all members without the CEO role or bot role
            bot_member = ctx.guild.me  # Get the bot's member instance
            for member in channel.members:
                if ceo_role not in member.roles and member != bot_member:
                    try:
                        await member.kick(reason="Channel closed by a CEO.")
                        await ctx.send(f"{member.mention} has been kicked.")
                    except discord.Forbidden:
                        await ctx.send(f"Failed to kick {member.mention}: Insufficient permissions.")
                    except discord.HTTPException as e:
                        await ctx.send(f"Failed to kick {member.mention}: {e}")

            # Delete the channel
            await channel.delete(reason="Channel closed by a CEO.")
        else:
            await ctx.send("You do not have permission to close this channel.")
    else:
        await ctx.send("This command can only be used in the 'Requests' category.")


# Run the bot with your token
bot.run(secret_key)
