# WaliTheBot Documentation

## Overview

Wali is a versatile Discord bot designed to enhance the functionality and interactivity of Discord servers. It leverages the power of AI through Google Gemini large languages of model to perform a wide range of tasks by processing natural language into discord commands, from managing server roles and permissions to banning, kicking, timing out, muting and deleting messages.

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

## Contributing

Contributions to Wali are welcome! Please follow the standard fork-and-pull request workflow. Ensure your code adheres to the project's coding standards and include documentation for new features or changes.

## License

Wali is licensed under a custom license. For more details, refer to the README.md file.

## Support

For support, questions, or feedback, please open an issue.

This documentation provides a comprehensive overview of Wali. For further details or specific use cases, refer to the source code or contact me(For the time being just open an issue).
