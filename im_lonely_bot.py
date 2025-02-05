import discord
import json
from discord import app_commands
from discord.ext import commands

# TOKEN = os.environ.get("DISCORD_TOKEN")  # Get token from environment variable
# NOTIFICATION_CHANNEL_ID = int(os.environ.get("1313426792295563295"))

notification_channels = {}
DEFAULT_CHANNEL_NAME = "general"  # Set the default channel name

intents = discord.Intents.default()
intents.message_content = True  # If you need to read messages later
intents.voice_states = True  # Enable the Voice States intent

# Use commands.Bot instead of discord.Client for command support
client = commands.Bot(command_prefix="!", intents=intents)


def load_guild_data():
    try:
        with open("guild_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


async def save_guild_data(guild_data):
    with open("guild_data.json", "w") as file:
        json.dump(guild_data, file, indent=4)



@client.event
async def on_ready():
    print(f'{client.user} has connected to Discord!')

    # Create a dictionary to store guild data
    guild_data = {}

    for guild in client.guilds:  # Iterate through all the guilds the bot is in
        guild_info = {
            "name": guild.name,
            "text_channels": [],
            "voice_channels": []
        }

        # Add text channels
        for channel in guild.text_channels:
            guild_info["text_channels"].append({
                "name": channel.name,
                "id": channel.id
            })

        # Add voice channels
        for channel in guild.voice_channels:
            guild_info["voice_channels"].append({
                "name": channel.name,
                "id": channel.id
            })

        # Add guild info to the main dictionary, using the guild ID as the key
        guild_data[str(guild.id)] = guild_info

    # Save the data to a JSON file
    with open("guild_data.json", "w") as file:
        json.dump(guild_data, file, indent=4)  # Use indent for pretty-printing

    print("Data has been saved to guild_data.json")

    # Sync slash commands
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")


@client.event
async def on_voice_state_update(member, before, after):
    if before.channel is None and after.channel is not None:  # User joined a voice channel
        voice_channel = after.channel
        members_in_channel = voice_channel.members

        if len(members_in_channel) == 1:  # Check if the user is alone
            notification_channel = client.get_channel(1336731836596093081)
            if notification_channel:
                await notification_channel.send(f"{member.mention} has joined {voice_channel.name} and is all alone! 🥺")
            else:
                print(f"Error: Notification channel with ID {1336731836596093081} not found.")


# Slash command to get a channel ID by its name
@client.tree.command(name="set_notification_room", description="Set the text room you want the notifications to go to.")
@app_commands.describe(channel_name="The name of the channel you want to set.")
@app_commands.checks.has_permissions(manage_channels=True)
async def set_notification_room(interaction: discord.Interaction, channel_name: str):
    pass  # Placeholder - Define the function's content here

async def get_channel_id(interaction: discord.Interaction, channel_name: str):
    # Load the JSON file
    try:
        with open("guild_data.json", "r") as file:
            guild_data = json.load(file)
    except FileNotFoundError:
        await interaction.response.send_message(
            "The guild data file does not exist. Please run the bot to generate it.", ephemeral=True)
        return

    # Get the current server's ID
    server_id = str(interaction.guild.id)

    # Check if the server's data exists in the file
    if server_id not in guild_data:
        await interaction.response.send_message(f"Server data for this guild (ID: {server_id}) not found in the file.",
                                                ephemeral=True)
        return

    # Search for the channel in text channels
    for channel in guild_data[server_id]["text_channels"]:
        if channel["name"].lower() == channel_name.lower():
            # nedi id w ndiro howa channel li yeba3tho liha


            await interaction.response.send_message(
                f"The ID for text channel **{channel['name']}** is `{channel['id']}`.", ephemeral=True)

            return

    # Search for the channel in voice channels
    for channel in guild_data[server_id]["voice_channels"]:
        if channel["name"].lower() == channel_name.lower():

            guild_data[server_id]["notifications_room"] = channel["id"]
            save_guild_data(guild_data)

            await interaction.response.send_message(
                f"The ID for voice channel **{channel['name']}** is `{channel['id']}`.", ephemeral=True)
            return

    # If the channel is not found
    await interaction.response.send_message(f"No channel with the name **{channel_name}** was found in this server.",
                                            ephemeral=True)


# Run the bot
client.run("MTMzNjcxNDEzOTYyMzQ4OTU1Ng.Gfyn18.gPVFxATHkPnZZxRmelVNr6UUfOKIN3G-gqH9ZA")