import discord
import traceback
import sys

def onInteractionErrors(client):
    @client.event
    async def on_error(event, *args, **kwargs):
        print(f"{event}")
        print(f"{args}")
        print(f"{kwargs}")

        exc_type, exc_value, exc_traceback = sys.exc_info()

        traceback.print_exception(exc_type, exc_value, exc_traceback)