I initially designed Wal-i to be a Discord bot to showcase my understanding of using LLM models and how to take full advantage of AI. However, I am now planning to develop it into a full-featured bot with moderation capabilities, as I want to create and manage my own Discord server. While the LLM part is functional, the full bot is still a work in progress.

Wal-i uses the Google Gemini API to transform user natural language requests into commands that the Python code can interpret and perform actions in a Discord server using discord.py. The project includes a file named ai_studio_api_call.py that I use to test my prompts before adding them to fine_tuning_instructions.csv for tuning a model in Google AI Studio. Currently, the bot can delete messages based on parameters like dates, before and after messages, the user or role who sent the message, specific keywords, or the channel in which the message was sent. It can also create channels and modify channel permissions.

Since the project is ongoing, here's some of the features I aim to implement:

Onboarding module: This will welcome new users and ask them for a password that has been shared with them, ideal for small servers with restricted access. 

The modules will stores any necessary data about a specific server using Discord embeds in a channel dedicated for every modules that only the server owner can access, minimizing the need for a database. You can see an example of this in onboarding.py. The onboarding module can be toggled on and off based on the description of an embed.
I know it risky to store data on messages, but since I will make sure every permission on those channel will be false, and I would be the one having access to them, I am confident that it will work. Anyway if I am stupid enough to put my data at risk even if it was a database I would still do it.

The only time I will use a database is when I need to give the LLM context of the previous requests made so it can do it work efficiently. Also I saw that the bot is faster to respond when I am retrieving data from the messages than from a database.

Google Safe Browsing API integration: This will check links shared in the server for safety.

Moderator module: Instead of granting direct permissions on the server to moderators like ban, mute etc..., this module will allow moderators to manage server tasks through Wal-i. The bot will verify if a moderator's request aligns with their permissions by referencing to a "moderator card" that will be stored in a message that any server owner can create and choose what wal-i will accept to do from it moderator and will reject if the actions the mod is asking aren't part of his mod card.

Harmful language detection: This module will check messages for harmful language or allow users to report such language, utilizing the Google Perspective API.

And more.

To reproduce this project, you need access to the Discord API, discord.py, the Gemini API, and the rest is listed in the requirements file, also you should make sure to run that in a virtual environement.

I plan to use a tunned model of the gemini llm in the future, so right now I'm using Google Cloud OAuth to facilitate this transition instead of an API key, since when the time come for me to use the tunned model I will need to access user data and google won't let me access that data just throught the API key. But you can create an account on Google AI Studio, obtain a Gemini API key, and the bot should work as expected by just changing the part of the code in ai_studio_api_call.py that uses load_creds instead of an api key. 
