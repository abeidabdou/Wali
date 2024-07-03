# WaliTheBot Documentation

## Overview

Wali is a versatile Discord bot designed to enhance the functionality and interactivity of Discord servers. It leverages the power of AI through Google Gemini large languages of model to perform a wide range of tasks by processing natural language into discord commands, from managing server roles and permissions to banning, kicking, timing out, muting and deleting messages.

I am not using json for the command retrieval, you should like at the ai studio file to see how the Language Model is giving out the commands
I also remarked that instead of giving different kind of example to explain what I need fro the LLM, repeating the same example also helped.(Don't know why)

## Features

- **AI-Powered Interactions:** Utilize AI to generate commands as responses to user queries from natural language.
- **Server Management:** Edit members, role management, and deleting messages.

## Setup

### Prerequisites

- Python 3.8 or higher
- Bot token from Discord Developer Portal
- Redis database for context keeping (Optional)
- And your Gemini API token (go in google ai studio to generate one)

### Installation

1. Clone the repository to your local machine.
   ```sh
   git clone https://github.com/abeidabdou/Wali
   ```
2. Set Up Python Environment and activate it
   ```sh
   python -m venv .venv
   ```   
4. Install the required dependencies by running `pip install -r requirements.txt` in your terminal.
   ```sh
   pip install -r requirements.txt
   ```
6. Run `wali.py` to start the bot: `python wali.py`.
7. A docker file is included if you want to use docker
   Build the Docker image by running:
   ```sh
   docker build -t wali-bot .
   ```
   And this will start the bot inside a your container
   ```sh
   docker run -d -p 7860:7860 wali-bot
   ```
   
### Configuration

- **Environment Variables:** Configure the bot using the `.env` file. Essential variables include `BOT_TOKEN`.
- **AI Studio API:** Set up the AI Studio API by configuring `ai_studio_api_call.py` with your API credentials in your env variable, I am using load creds but you can use the Gemini API directly
- **Redis:** I am using redis for context keeping, so if you want to use it you will need redis credentials from [redis lab](https://redis.io/) 

## Usage

### Commands

- **Invoke Wali:** Use the `/wal_i` command followed by your request to interact with the bot.
- **Setup Wali:** Use the `/wal_i_setup` command to configure the bot for your server.

### Adding Commands

1. Create a new Python file in the `command/` directory for your command.
2. Implement your command function with the required logic.
3. After that your command should be available to be called by `loadCommand.py` to make it available for dynamic invocation.

### AI-Powered Interactions

Read the `ai_studio_api_call.py` prompts to understand how the commands are structured

## Architecture

Wali is built on the Discord.py library and structured around a modular command system. The bot's functionality is divided into several components:

- **Command Handlers:** Located in the `command/` directory, these handle specific actions like sending messages or editing member roles.
- **Event Listeners:** Defined in the `events/` directory, these listen for and respond to events like messages or reactions.
- **Parameters:** Stored in the `parameters/` directory, these configure the bot's behavior, such as language settings.
- **Context Management:** The `context.py` file manages user requests for context keeping, facilitating personalized interactions.

## So What Can WAL-I Do?

> The command can only be used by server owners you can change that

### Commands

Since WAL-I doesn't use any specific command to perform actions but relies on natural language, we will go through examples.

**Everything you will see are just examples, you can ask Wal-i what you want him to do in whatever way you want as long as he can do it. You just need to be precise on what you want him to do amd not assume he will understand you by magic**

#### 1. Deleting Messages

WAL-I can delete messages based on various criteria: by user, keywords, links, attachments, time intervals, and message IDs. Deletion can also be scoped to specific channels or all channels for server owners.

It all start with this command /wal_i then your request

**1.1 Deleting Messages by ID:**

```diff
- "Delete this message to ensure privacy. 32109876"
- "WAL-I, this message needs to be removed, 23424234, 32109876, user doesn't respect the rules"
```

**1.2 Deleting Messages by Channel:**

```diff
- "delete the last 30 messages in test"
- "delete the last 20 messages"
```
_(WAL-I assumes the current channel if none is specified)_

```diff
- "delete the last 20 messages sent here"
- "delete the last 50 messages in all channels" 
```

_(And you will always need a limit, you can specify that limit to none please be carefull with that)_
_(And you will always need a reason, I am just bypassing that here to just show the examples)_

**1.3 Deleting Messages by Interval:**

```diff
- "Delete the 10 messages sent before 23423424532 in test"
- "delete the last 10 messages sent after 2375672242"
- "delete the messages sent after 2375672242 and before 23423424532 in channel test"
- "delete the messages sent between 2375672242 and 23423424532 in channel test"
```
_(Notice in the last one I didn't have to specify which one is the before and which one is the after message ID)_
_(When deleting messages where there's a before or after message and they are a message id you don't really need to specify the channel)_
_(Which means the following could just also work)_

```diff
- "Delete the 10 messages sent before 23423424532"
- "delete the last 10 messages sent after 2375672242"
- "delete the messages sent after 2375672242 and before 23423424532"
- "delete the messages sent between 2375672242 and 23423424532"
```

_(Interval can also be date and time available only to server owners, here you will need to specify a channel)_
_(please be carefull here, always make sure you give the correct date and time)_
_(If no date is given the Wal-i assume that it's the same day, and if no time is given he will also assume the time to be midnight)_
_(WAL-I uses the international timezone)_

```diff
- "Delete the 10 messages sent before the 1 january 2030 at 2am in general"
- "delete the messages sent after 1 january 2030 at 2am and before 2 january 2030  in all channels"
- "delete messages sent between 2am and 5pm in general"
```

_(When both before and after are present the limit is not taken into consideration)_

**1.4 Deleting Messages with Attachments:**

_(for the time being available attachements are (Links, video and Image)_

```diff
- "delete all messages with link"
- "delete any message with an image in channel test"
```

**1.5 Deleting Messages with Specific Words or Keywords:**

```diff
- "Delete any message containing this emoji 🫡"
- "Delete any message with stp in it"
```

**1.6 Deleting Messages by members:**

```diff
- "delete the last 10 messages Ali sent"
- "delete the last 10 messages Ali sent in test"
- "delete the last 10 messages I sent in channel test"
- "delete the last 10 messages I sent in all channels"
```

```diff
- "Delete the 20 messages Ali sent before 23423424532 in channel test"
- "delete messages sent by Ali after 23453534536 and before 23423424532"
- "delete messages with stp in channel test sent by Ali before this message 23453534536"
```

**Combining Criteria:**

_(All the criteria above can be combined, you just need to respect the rules of those criteria)_

```diff
- "Delete messages sent by Ali and Sam containing the word trip, limit none. They are being disrespectful"
```

WAL-I provides targeted message deletion capabilities with an emphasis on specificity. If he can't fulfill a request, he will notify you.

#### 2. Moderation Actions

WAL-I can ban, kick, timeout, mute, and unmute one or multiple users.

_(And you will always need to give a reason)_

```diff
- "WAL-I ban Amy"
- "WAL-I ban Amy, Samy, and Ali"
```

#### 3. Role Permissions

WAL-I can assign role permissions in a channel.

```diff
- "WAL-I let everyone send messages in test"
```
_(This grants @everyone the permission to send messages in channel test)_

**Important Notes:**

```diff
! Specificity is key.
! You can combine all the creterias listed here when making a request.
! If no limit is provided, he will ask for one.
! No limit is needed when using before and after criteria.
! A reason must be provided for all deletions, banning, timing out or kicking.
! When timimg out, if there's no specific time provided the limit will be 1 DAY
! Timeout duration valid options are: 60 SECS, 5 MINS, 10 MINS, 1 HOUR, 1 DAY, and 1 WEEK
! When banning a member you can also delete the messages he sent in the server
! Message deletion valid options when banning a member: Previous Hour, Previous 6 Hours, Previous 12 Hours, Previous 24 Hours, Previous 3 Days, Previous 7 Days
! Somehting like this "ban ali and delete all the messages he sent in the last 24h. He was being disrespectful"
```

## Contributing

Contributions to Wali are welcome! Please follow the standard fork-and-pull request workflow. Ensure your code adheres to the project's coding standards and include documentation for new features or changes.

## License

WaliTheBot © 2024 by Al-abeid Abdou Soimadou is licensed under CC BY-NC-SA 4.0. To view a copy of this license, visit https://creativecommons.org/licenses/by-nc-sa/4.0/

## Support

For support, questions, or feedback, please open an issue.

This documentation provides a comprehensive overview of Wali. For further details or specific use cases, refer to the source code or contact me(For the time being just open an issue).
