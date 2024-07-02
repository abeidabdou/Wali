import json

def guildLanguage(guild):
        
    guild_language = "en-US"

    with open(f"languages/{guild_language}.json", 'r', encoding='utf-8') as file:
        language = json.load(file)

    return language