import discord
import json
from discord import app_commands
from discord.ext import commands

notification_channels = {}
DEFAULT_CHANNEL_NAME = "general"  # Set the default channel name

intents = discord.Intents.default()
intents.message_content = True  # If you need to read messages later
intents.voice_states = True  # Enable the Voice States intent
intents.guilds = True
intents.members = True

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

    guild_data = load_guild_data()

    for guild in client.guilds:
        guild_id = str(guild.id)

        if guild_id not in guild_data:
            # Add new guild data (same as before)
            guild_info = {
                "name": guild.name,
                "notifications_channel_id": None,
                "text_channels": [],
                "voice_channels": []
            }

            for channel in guild.text_channels:
                guild_info["text_channels"].append({"name": channel.name, "id": channel.id})

            for channel in guild.voice_channels:
                guild_info["voice_channels"].append({"name": channel.name, "id": channel.id})

            guild_data[str(guild.id)] = guild_info
            print(f"Added data for {guild.name}")  # Indicate new guild data
        else:  # Update existing guild data if needed
            saved_text_channels = {c['id']: c['name'] for c in guild_data[guild_id]['text_channels']}
            saved_voice_channels = {c['id']: c['name'] for c in guild_data[guild_id]['voice_channels']}

            current_text_channels = {c.id: c.name for c in guild.text_channels}
            current_voice_channels = {c.id: c.name for c in guild.voice_channels}

            if saved_text_channels != current_text_channels or saved_voice_channels != current_voice_channels:
                # await _update_channel_lists(guild)
                guild_id = str(guild.id)

                if guild_data[guild_id]["notifications_channel_id"] not in current_text_channels:
                    guild_data[guild_id]["notifications_channel_id"] = None

                # Update text channels
                guild_data[guild_id]["text_channels"] = [
                    {"name": channel.name, "id": channel.id} for channel in guild.text_channels
                ]

                # Update voice channels
                guild_data[guild_id]["voice_channels"] = [
                    {"name": channel.name, "id": channel.id} for channel in guild.voice_channels
                ]
                print(f"Channel lists updated for guild {guild.name}")

            if "excluded_users" in guild_data[guild_id]:
                excluded_users_to_remove = []
                for user_id in guild_data[guild_id]["excluded_users"]:
                    member = guild.get_member(user_id)  # Try to get the member object
                    if member is None:  # Member is no longer in the guild
                        excluded_users_to_remove.append(user_id)

                for user_id in excluded_users_to_remove:
                    guild_data[guild_id]["excluded_users"].remove(user_id)
                    print(
                        f"User (ID: {user_id}) removed from excluded users in guild {guild.name} (no longer in guild).")

                # Check and reset notification channel if deleted
                if guild_data[guild_id].get("notifications_channel_id"):
                    notification_channel_id = int(guild_data[guild_id]["notifications_channel_id"])
                    notification_channel = client.get_channel(notification_channel_id)
                    if notification_channel is None:  # Channel doesn't exist anymore
                        guild_data[guild_id]["notifications_channel_id"] = None
                        await save_guild_data(guild_data)
                        print(f"Notification channel reset for guild {guild.name} (deleted).")

    await save_guild_data(guild_data)
    print("Data has been loaded/synced to guild_data.json")

    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")



@client.event
async def on_voice_state_update(member, before, after):
    guild_data = load_guild_data()
    guild_id = str(member.guild.id)

    if guild_id in guild_data and not guild_data[guild_id].get("notifications_paused", False):  # Check notifications paused
        if before.channel is None and after.channel is not None:
            voice_channel = after.channel
            members_in_channel = voice_channel.members

            if len(members_in_channel) == 1:
                notification_channel = None
                try:
                    with open("guild_data.json", "r") as file:
                        guild_data = json.load(file)
                        server_id = str(member.guild.id)
                        notification_channel_id = guild_data[server_id]["notifications_channel_id"]
                        notification_channel = client.get_channel(notification_channel_id)

                except FileNotFoundError:
                    await interaction.response.send_message(
                        "The guild data file does not exist. Please run the bot to generate it.", ephemeral=True)
                    return

                if notification_channel is not None:
                    await notification_channel.send(f"{member.mention} has joined {voice_channel.name} and is all alone! 🥺")
                else:
                    print(f"Error: Notification channel is not set yet, please se it using the /set_notifications_channel command")



# Slash command to get a channel ID by its name
@client.tree.command(name="set_notifications_channel", description="Get the ID of a channel by its name.")
@app_commands.describe(channel_name="The name of the channel to search for.")
async def get_channel_id(interaction: discord.Interaction, channel_name: str):
    # Load the JSON file
    try:
        with open("guild_data.json", "r") as file:
            guild_data = json.load(file)
    except FileNotFoundError:
        await interaction.response.send_message("The guild data file does not exist. Please run the bot to generate it.", ephemeral=True)
        return

    # Get the current server's ID
    server_id = str(interaction.guild.id)

    # Check if the server's data exists in the file
    if server_id not in guild_data:
        await interaction.response.send_message(f"Server data for this guild (ID: {server_id}) not found in the file.", ephemeral=True)
        return

    # Search for the channel in text channels
    for channel in guild_data[server_id]["text_channels"]:
        if channel["name"].lower() == channel_name.lower():

            guild_data[server_id]["notifications_channel_id"] = channel["id"]
            await save_guild_data(guild_data)
            await interaction.response.send_message(f"The ID for text channel **{channel['name']}** is `{channel['id']}`.", ephemeral=True)
            return

    # Search for the channel in voice channels
    for channel in guild_data[server_id]["voice_channels"]:
        if channel["name"].lower() == channel_name.lower():
            await interaction.response.send_message(f"The ID for voice channel **{channel['name']}** is `{channel['id']}`.", ephemeral=True)
            return

    # If the channel is not found
    await interaction.response.send_message(f"No channel with the name **{channel_name}** was found in this server.", ephemeral=True)



def load_guild_data():
    try:
        with open("guild_data.json", "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}

async def save_guild_data(guild_data):
    with open("guild_data.json", "w") as file:
        json.dump(guild_data, file, indent=4)


async def _load_and_sync_data(): # New function to load and sync data
    guild_data = load_guild_data()
    for guild in client.guilds:
        if str(guild.id) not in guild_data:
            await _add_guild_data(guild, guild_data) # Call function to add data
    await save_guild_data(guild_data)
    print("Data has been loaded/synced to guild_data.json")


async def _add_guild_data(guild, guild_data): # New function to add data
    guild_info = {
        "name": guild.name,
        "notifications_channel_id": None,
        "text_channels": [],
        "voice_channels": []
    }

    for channel in guild.text_channels:
        guild_info["text_channels"].append({"name": channel.name, "id": channel.id})

    for channel in guild.voice_channels:
        guild_info["voice_channels"].append({"name": channel.name, "id": channel.id})

    guild_data[str(guild.id)] = guild_info
    print(f"Added data for {guild.name}")


async def _update_channel_lists(guild):


    guild_data = load_guild_data()  # Load data FIRST
    guild_id = str(guild.id)

    if guild_id in guild_data:
        guild_data[guild_id]["text_channels"] = []  # Clear existing text channels
        guild_data[guild_id]["voice_channels"] = []  # Clear existing voice channels
        print(guild_id)
        for channel in guild.text_channels:
            guild_data[guild_id]["text_channels"].append({"name": channel.name, "id": channel.id})

        for channel in guild.voice_channels:
            guild_data[guild_id]["voice_channels"].append({"name": channel.name, "id": channel.id})

        await save_guild_data(guild_data)  # Save AFTER updating
        print(f"Channel lists updated for guild {guild.name}")


@client.event
async def on_guild_channel_create(channel):
    guild = channel.guild
    await _update_channel_lists(guild)
    print(f"Channel '{channel.name}' created in guild '{guild.name}'. Channel lists updated.")

@client.event
async def on_guild_channel_delete(channel):
    guild = channel.guild
    await _update_channel_lists(guild)
    print(f"Channel '{channel.name}' deleted in guild '{guild.name}'. Channel lists updated.")
    if channel.id == load_guild_data().get(str(guild.id), {}).get("notifications_channel_id"):
        new_data = load_guild_data()
        new_data[str(guild.id)]["notifications_channel_id"] = None
        await save_guild_data(new_data)



@client.event  # The crucial addition is the on_guild_join handler
async def on_guild_join(guild):
    guild_data = load_guild_data()  # Load existing data
    await _add_guild_data(guild, guild_data) # Call function to add data
    await save_guild_data(guild_data)  # Save the updated data
    print(f"Data added for newly joined guild: {guild.name}")

@client.event
async def on_guild_remove(guild):  # The crucial addition: on_guild_remove
    guild_data = load_guild_data()
    guild_id = str(guild.id)

    if guild_id in guild_data:
        del guild_data[guild_id]  # Remove the guild's data from the dictionary
        await save_guild_data(guild_data)  # Save the updated data
        print(f"Data deleted for guild: {guild.name} (ID: {guild.id})")
    else:
        print(f"No data found for guild: {guild.name} (ID: {guild.id})")



@client.tree.command(name="exclude_user", description="Exclude a user from alone notifications.")
@app_commands.describe(user="The user to exclude.")
async def exclude_user(interaction: discord.Interaction, user: discord.Member):
    guild_data = load_guild_data()
    guild_id = str(interaction.guild.id)

    if guild_id not in guild_data:
        guild_data[guild_id] = {}  # Create guild data if it doesn't exist

    if "excluded_users" not in guild_data[guild_id]:
        guild_data[guild_id]["excluded_users"] = []

    if user.id not in guild_data[guild_id]["excluded_users"]:
        guild_data[guild_id]["excluded_users"].append(user.id)
        await save_guild_data(guild_data)
        await interaction.response.send_message(f"{user.mention} will no longer trigger alone notifications in this server.", ephemeral=True)
    else:
        await interaction.response.send_message(f"{user.mention} is already excluded in this server.", ephemeral=True)



@client.tree.command(name="include_user", description="Include a user in alone notifications.")
@app_commands.describe(user="The user to include.")
async def include_user(interaction: discord.Interaction, user: discord.Member):
    guild_data = load_guild_data()
    guild_id = str(interaction.guild.id)

    if guild_id in guild_data and "excluded_users" in guild_data[guild_id]:
        if user.id in guild_data[guild_id]["excluded_users"]:
            guild_data[guild_id]["excluded_users"].remove(user.id)
            await save_guild_data(guild_data)
            await interaction.response.send_message(f"{user.mention} will now trigger alone notifications in this server.", ephemeral=True)
        else:
            await interaction.response.send_message(f"{user.mention} is not currently excluded in this server.", ephemeral=True)
    else:
        await interaction.response.send_message(f"No excluded users found for this server.", ephemeral=True)


@client.event
async def on_raw_member_remove(event):  # Use on_raw_member_remove
    guild_id = str(event.guild_id)  # Get guild ID from the event
    user_id = event.user.id  # Get user ID from the event

    guild_data = load_guild_data()

    if guild_id in guild_data and "excluded_users" in guild_data[guild_id]:
        if user_id in guild_data[guild_id]["excluded_users"]:
            guild_data[guild_id]["excluded_users"].remove(user_id)
            await save_guild_data(guild_data)
            print(f"User (ID: {user_id}) removed from excluded users in guild (ID: {guild_id}) (member removed).")

            # Optionally, reset notification channel if it was the removed user
            if guild_data[guild_id].get("notifications_channel_id") == str(user_id):
                guild_data[guild_id]["notifications_channel_id"] = None
                await save_guild_data(guild_data)
                print(f"Notification channel reset in guild (ID: {guild_id}) (was the removed user).")







@client.tree.command(name="pause_notifications", description="Pause notifications for this server.")
async def pause_notifications(interaction: discord.Interaction):
    guild_data = load_guild_data()
    guild_id = str(interaction.guild.id)

    if guild_id not in guild_data:
        guild_data[guild_id] = {}

    if not guild_data[guild_id].get("notifications_paused", False):  # Check the notifications paused state
        guild_data[guild_id]["notifications_paused"] = True
        await save_guild_data(guild_data)
        await interaction.response.send_message("Notifications are now paused in this server.", ephemeral=True)
        print(f"Notifications paused in guild {interaction.guild.name}.")
    else:
        await interaction.response.send_message("Notifications are already paused in this server.", ephemeral=True)

@client.tree.command(name="resume_notifications", description="Resume notifications for this server.")
async def resume_notifications(interaction: discord.Interaction):
    guild_data = load_guild_data()
    guild_id = str(interaction.guild.id)

    if guild_id not in guild_data:
        guild_data[guild_id] = {}

    if guild_data[guild_id].get("notifications_paused", False):  # Check the notifications paused state
        guild_data[guild_id]["notifications_paused"] = False
        await save_guild_data(guild_data)
        await interaction.response.send_message("Notifications are now resumed in this server.", ephemeral=True)
        print(f"Notifications resumed in guild {interaction.guild.name}.")
    else:
        await interaction.response.send_message("Notifications are already running in this server.", ephemeral=True)






# Run the bot
client.run("Token")
