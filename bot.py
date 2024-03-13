from dotenv import load_dotenv
from discord.ext import commands
from discord.ui import Button
from discord import ButtonStyle
from PIL import Image
import discord, os, re, asyncio, sys, io

load_dotenv()
CLIENT_TOKEN = os.getenv("CLIENT_TOKEN")

intents = discord.Intents.default()
intents.message_content = True
client = commands.Bot(command_prefix="r!", intents=intents)

class ImageButtons(discord.ui.View):
    def __init__(self, filenames):
        super().__init__()
        self.filenames = filenames
        for i, file in enumerate(filenames):
            self.add_item(Button(style=ButtonStyle.primary, label=f"Vote {i}", custom_id=file, row=i // 2))
        self.add_item(Button(style=ButtonStyle.primary, label="None are good", custom_id="none", row=2))
        for item in self.children:
            item.callback = self.dispatch
    async def dispatch(self, interaction: discord.Interaction):
        custom_id = interaction.data["custom_id"]
        message = interaction.message
        userid = interaction.user.id

        for file in self.filenames:
            if(file != custom_id or custom_id == "none"):
                os.remove(f"./images/{file}")
        
        await message.edit(content="", view=None)
        self.stop()


@client.event
async def on_ready():
    print(f"Logged in as {client}")
    try:
        synced = await client.tree.sync()
        print(f"Synced {len(synced)} command(s).")
    except Exception as e:
        print(e)
        sys.exit()

@client.tree.command(name="rate")
async def chat(interaction: discord.Interaction):
    await interaction.response.defer()
    
    # list out all the images
    files = os.listdir("./images")
    for file in files:
        if(not os.path.isfile(os.path.join("./images", file))):
            files.remove(file)
            continue
        if(not "png" in file):
            files.remove(file)
    files.sort()
    
    # loop through them
    while len(files) > 0:
        # get four images with same parameters
        compared_files = [files.pop(0) for _ in range(4)]

        # put them into discord file format
        discord_files = []
        for file in compared_files:
            image = Image.open(f"./images/{file}")
            with io.BytesIO() as image_binary:
                image.save(image_binary, "PNG")
                image_binary.seek(0)
                discord_file = discord.File(fp=image_binary, filename=file)
            discord_files.append(discord_file)
        
        # create view
        view = ImageButtons(compared_files)

        await interaction.followup.send(content="Borpa", view=view, files=discord_files)
        await view.wait()
        
client.run(CLIENT_TOKEN)