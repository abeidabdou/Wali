
def onMessage(client):
    @client.event
    async def on_message(message):
        if message.author == client.user:
            return

        if "wal-i" in message.channel.name and message.channel.name != "wal-i-mods-channel":
            await message.delete()
