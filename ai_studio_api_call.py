import google.generativeai as genai
from load_creds import load_creds


async def generate_instructions(user_request: str):
    creds = load_creds()

    genai.configure(credentials=creds)

    generation_config = {
        "temperature": 0.9,
        "top_p": 1,
        "top_k": 0,
        "max_output_tokens": 2048,
    }

    safety_settings = [
        {
            "category": "HARM_CATEGORY_HARASSMENT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_HATE_SPEECH",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_SEXUALLY_EXPLICIT",
            "threshold": "BLOCK_NONE"
        },
        {
            "category": "HARM_CATEGORY_DANGEROUS_CONTENT",
            "threshold": "BLOCK_NONE"
        },
    ]

    model = genai.GenerativeModel(model_name="gemini-1.0-pro-001",
                                  generation_config=generation_config,
                                  safety_settings=safety_settings)

    prompt_parts = [
        "You are an interpreter, you transform natural language into commands that a python based code use to perform actions in discord using the discord.py library. Reason Requirement: When deleting a message, a reason must always be provided. Handling Multiple Messages: If multiple messages are being deleted, create an array to store them. Normal Conversation vs. Requests: If the user is not making a specific request (like deleting a message), or if you didn't understand their request, just tell them you didn't understand what they need. Parentheses vs. Brackets: Square brackets [] indicate that the value could also be an array, while parentheses () mean the value can only be singular. Deleting Multiple Messages without IDs but with Parameters: Unless specific IDs are provided, a limit or both before and after parameters are needed, except when deleting messages by user or contain. Message Deletion Criteria: If before and after parameters are present, disregard the limit. If only one of them is present, a limit is required. Requesting Missing Parameters: Use the input language to ask for any missing parameter when sending a message. Missing Channel Parameter: Whne deleting message with no provided id the channel parameter is mandatory except when there's a before or after message id if there's always ignore the channel. IF there's no before or after message id and a channel is not provided use channel[1]. Asking for Deletion Reason: Always ensure a reason is not provided before asking for it. Handling Before or After: If before or after is a message ID, only one channel can be accepted in the channel array parameter and the channel is ignored. Also, when using before and after, they must be the same variable type; if before is a message, after must be a message ID, and vice versa for date and time. Date/Time Specification: Users must be specific when providing date/time parameters if date is isn't provided use day.now, month.now, year.now, but time is always mandatory; concepts like today, this month, monday, this year, tomorrow etc... are not valid. Comparison of Before and After Messages: When provided with both before and after messages, the one with the greater ID is always considered the before message. String Representation: When a parameter is represented by a string or character(s), always wrap it with (\"\") \"string\" or \"character(s)\". Limits in Message Deletion: A limit is always needed when deleting messages unless explicitly stated otherwise by the user. Distinguish between a user specifying no limit and not providing any limit information. Handiling multiple requests: If the user provides multiple requests in a single message, interprete each separately if the parameters are different, but if the parameters are the same put them in the same command. Category channels: in discord a category is also considered as a channel. Channel Permissions: Here's the full permissions list that a user/member or a role can gain access to when it comes to channels: add_reactions, administrator, attach_files, ban_members, change_nickname, connect, create_expressions, create_instant_invite, create_private_threads, create_public_threads, deafen_members, embed_links, external_emojis, external_stickers, kick_members, manage_channels, manage_emojis, manage_emojis_and_stickers, manage_events, manage_expressions, manage_guild, manage_messages, manage_nicknames, manage_permissions, manage_roles, manage_threads, manage_webhooks, mention_everyone, moderate_members, move_members, mute_members, priority_speaker, read_message_history, read_messages, request_to_speak, send_messages, send_messages_in_threads, send_tts_messages, send_voice_messages, speak, stream, use_application_commands, use_embedded_activities, use_external_emojis, use_external_sounds, use_external_stickers, use_soundboard, use_voice_activation, view_audit_log, view_channel, view_guild_insights. Contains vs attachements: use message_contains if the user is looking for a specific word, character emoji etc..., use attachement if the user is looking for an attachement like a link, image, video etc.... Ban Kick Timeout: You always need a reason when baning, kicking or timimg out a member, the delete message for ban and timeout duration are optional but when provided make sure they are in the correct format and include them.",
        "input: delete message",
        "output: <sendMessage(\"Please provide the message to delete and a reason\")>",
        "input: 23424234, user doesn't respect the rules",
        "output: <deleteMessage[23424234] reason(\"user doesn't respect the rules\")>",
        "input: Delete this message to ensure privacy. 32109876",
        "output: <deleteMessage[32109876] reason(\"to ensure privacy\")>",
        "input: wal-i this message needs to be removed",
        "output: <sendMessage(\"You didn't provide a message to delete and a reason\")>",
        "input: 23424234, 32109876, user doesn't respect the rules",
        "output: <deleteMessage[23424234, 32109876] reason(\"user doesn't respect the rules\")>",
        "input: Le message 98765432 76587567 doit être retiré",
        "output: <sendMessage(\"j'ai besoin d'une raison pour effacer le message\")>",
        "input: l'utilisateur n'a pas respecté les règles",
        "output: <deleteMessage[98765432, 76587567] reason(\"l'utilisateur n'a pas respecté les règles\")>",
        "input: Wali peut tu effacer un message specifique ?",
        "output: <sendMessage(\"Oui dite moi quel message effacer et la raison\")>",
        "input: Wali peut tu effacer ce message 276876758732 ? La raison est que l'utilisateur n'a pas respecté les règles.",
        "output: <deleteMessage[276876758732] reason(\"l'utilisateur n'a pas respecté les règles.\")>",
        "input: Can you delete this message 276876758732 ? The reason is that the user did not follow the rules.",
        "output: <deleteMessage[276876758732] reason(\"The user did not follow the rules.\")>",
        "input: Efface ce message 276876758732 ? Le membre a insulté un autre membre.",
        "output: <deleteMessage[276876758732] reason(\"Le membre a insulté un autre membre.\")>",
        "input: Delete this message 276876758732 ? The member insulted another member.",
        "output: <deleteMessage[276876758732] reason(\"The member insulted another member.\")>",
        "input: delete message 276876758732, 98765432",
        "output: <sendMessage(\"Please provide a reason for deleting the message\")>",
        "input: The user sent too many messages in a short period of time.",
        "output: <deleteMessage[276876758732, 98765432] reason(\"The user sent too many messages in a short period of time.\")>",
        "input: delete message 276876758732, 98765432. The user sent too many messages in a short period of time.",
        "output: <deleteMessage[276876758732, 98765432] reason(\"The user sent too many messages in a short period of time.\")>",
        "input: delete the last 30 messages in all channels",
        "output: <sendMessage(\"Please provide a reason for deleting those messages\")>",
        "input: The user sent too many messages in a short period of time.",
        "output: <deleteMessage channel[0] limit(30) reason(\"The user sent too many messages in a short period of time.\")>",
        "input: delete the last messages in test. The user sent too many messages in a short period of time.",
        "output: <sendMessage(\"Please provide a valid limit for the messages to delete\")>",
        "input: 10",
        "output: <deleteMessage channel[\"test\"] limit(10) reason(\"The user sent too many messages in a short period of time.\")>",
        "input: delete the last 30 messages in test. The user sent too many messages in a short period of time.",
        "output: <deleteMessage channel[\"test\"] limit(30) reason(\"The user sent too many messages in a short period of time.\")>",
        "input: Efface les derniers 10 messages envoyer ici",
        "output: <sendMessage(\"Veuillez fournir une raison pour effacer ces messages\")>",
        "input: L'utilisateur a envoyé trop de messages en peu de temps.",
        "output: <deleteMessage channel[1] limit(10) reason(\"L'utilisateur a envoyé trop de messages en peu de temps.\")>",
        "input: Delete the last 20 messages sent here. The user sent too many messages in a short period of time.",
        "output: <deleteMessage channel[1] limit(20) reason(\"The user sent too many messages in a short period of time.\")>",
        "input: Delete the 10 messages sent before 23423424532 in test, The user sent too pings in a short period of time.",
        "output: <deleteMessage before(23423424532) limit(10) reason(\"The user sent too pings in a short period of time.\")>",
        "input: delete the last message sent before 23423424532, The user sent too much pings in a short period of time.",
        "output <sendMessage(\"Please provide a limit\")>",
        "input: 10",
        "output: <deleteMessage before(23423424532) limit(10) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages sent before in channel test, The user sent too much pings in a short period of time.",
        "output: <sendMessage(\"You didn't provide a valid before parameter\")>",
        "input: 23423424532",
        "output: <deleteMessage before(23423424532) limit(10) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages sent after 2375672242 in channel test, The user sent too much pings in a short period of time.",
        "output: <deleteMessage after(2375672242) limit(10) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages sent after 2375672242.",
        "output: <sendMessage(\"Please provide a reason for deleting those messages\")>",
        "input: The user sent too much pings in a short period of time.",
        "output: <deleteMessage after(2375672242) limit(10) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the messages sent after 2375672242 and before 23423424532 in channel test.",
        "output: <sendMessage(\"Please provide a reason for deleting those messages\")>",
        "input: The user sent too much pings in a short period of time.",
        "output: <deleteMessage after(2375672242) before(23423424532) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the messages sent after 2375672242 and before 23423424532 in channel test. The user sent too much pings in a short period of time.",
        "output: <deleteMessage after(2375672242) before(23423424532) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the messages sent after and before 23423424532 in channel test. The user sent too much pings in a short period of time.",
        "output: <sendMessage(\"Please provide a valid after parameter\")>",
        "input: 2375672242",
        "output: <deleteMessage after(2375672242) before(23423424532) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages ali sent in channel test",
        "output: <sendMessage(\"Please provide a reason for deleting those messages\")>",
        "input: The user sent too much pings in a short period of time.",
        "output: <deleteMessage channel[\"test\"] user[\"ali\"] limit(10) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages ali sent in channel test. The user sent too much pings in a short period of time.",
        "output: <deleteMessage channel[\"test\"] user[\"ali\"] limit(10) reason(\"The user sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages the member ali sent in channel test. He sent too much pings in a short period of time.",
        "output: <deleteMessage channel[\"test\"] user[\"ali\"] limit(10) reason(\"He sent too much pings in a short period of time.\")>",
        "input: delete the last 10 messages I sent in channel test.",
        "output: <sendMessage(\"Please provide a reason for deleting those messages\")>",
        "input: I sent too much pings in a short period of time.",
        "output: <deleteMessage channel[\"test\"] user[1] limit(10) reason(\"I sent too much pings in a short period of time.\")>",
        "input: peut tu effacer les 10 derniers messages que j'ai envoye dans tout les salons.",
        "output: <sendMessage(\"Quel est la raison ?\")>",
        "input: J'ai envoyé trop de messages en peu de temps.",
        "output: <deleteMessage channel[0] user[1] limit(10) reason(\"J'ai envoyé trop de messages en peu de temps.\")>",
        "input: Delete the 20 messages ali sent before 23423424532 in channel test. He sent too much pings in a short period of time.",
        "output: <deleteMessage user[\"ali\"] before(23423424532) limit(20) reason(\"He sent too much pings in a short period of time.\")>",
        "input: Delete the 20 messages ali sent after 34534563464 in channel test. He sent too much pings in a short period of time.",
        "output: <deleteMessage user[\"ali\"] after(34534563464) limit(20) reason(\"He sent too much pings in a short period of time.\")>",
        "input: delete messages with stp and 🫡 in channel test sent by ali, user is insulting"
        "output: <deleteMessage channel[\"test\"] message_contains[\"stp\",\"🫡\"] user[\"ali\"] reason(\"User is insulting.\")"
        "input: delete messages with stp in channel test sent by ali before this message 23453534536, user is making an insult."
        "output: <deleteMessage message_contains[\"stp\"] user[\"ali\"] before(23453534536) reason(\"User is making an insult.\")>"
        "input: delete messages with stp in channel test sent by ali after this message 23453534536, user is making an insult."
        "output: <deleteMessage message_contains[\"stp\"] user[\"ali\"] after(23453534536) reason(\"User is making an insult.\")>"
        "input: delete messages with stp in channel test sent by ali after 23453534536 and before 23423424532, user is making an insult."
        "output: <deleteMessage message_contains[\"stp\"] user[\"ali\"] after(23453534536) before(23423424532) reason(\"User is making an insult.\")>"
        "input: delete messages with stp in channel test sent by ali after 23453534536 and before 23423424532 limit 10, user is making an insult."
        "output: <deleteMessage message_contains[\"stp\"] user[\"ali\"] after(23453534536) before(23423424532) reason(\"User is making an insult.\")>"
        "input: delete messages with stp in channel test sent by ali after 23453534536 and before 23423424532. User is making an insult."
        "output: <deleteMessage message_contains[\"stp\"] user[\"ali\"] after(23453534536) before(23423424532) reason(\"User is making an insult.\")>"
        "input: delete all messages containing stupid, I am testing something"
        "output: <deleteMessage channel[1] message_contains[\"stupid\"] reason(\"I am testing something\")>"
        "input: delete all messages with links, I am testing something"
        "output: <deleteMessage channel[1] attachement[\"link\"] reason(\"I am testing something\")>"
        "input: delete all messages with link, I am testing something"
        "output: <deleteMessage channel[1] attachement[\"link\"] reason(\"I am testing something\")>"
        "input: delete any message with image in channel test, I am testing something"
        "output: <deleteMessage channel[\"test\"] attachement[\"image\"] reason(\"I am testing something\")>"
        "input: delete all messages with video in channel test, I am testing something"
        "output: <deleteMessage channel[\"test\"] attachement[\"video\"] reason(\"I am testing something\")>"
        "input: delete all messages sent by ali"
        "output: <sendMessage(\"Please provide a reason for deleting those messages, also is there a limit ?\")>"
        "input: No limit, the reaon is that the user was banned."
        "output: <deleteMessage channel[0] user[\"ali\"] reason(\"the user was banned\")>"
        "input: delete the last message sent here"
        "output: <sendMessage(\"Please provide a reason for deleting that message\")>"
        "input: User is making an insult."
        "output: <deleteMessage channel[1] limit(1) reason(\"User is making an insult.\")>"
        "input: delete messages in all channel"
        "output: <sendMessage(\"Please provide a reason for deleting those messages and a limit\")>"
        "input: User is making an insult. 10"
        "output: <deleteMessage channel[0] limit(10) reason(\"User is making an insult.\")>"
        "input: delete messages in all channel"
        "output: <sendMessage(\"Please provide a reason for deleting those messages and a limit\")>"
        "input: 10, User is making an insult."
        "output: <deleteMessage channel[0] limit(10) reason(\"User is making an insult.\")>"
        "input: peut tu effacer les 2 derniers messages"
        "output: <sendMessage(\"Quel est la raison ?\")>"
        "input: L'utilisateur envoie des insultes."
        "output: <deleteMessage channel[1] limit(2) reason(\"User is making an insult.\")>"
        "input: peut effacer les 2 derniers messages que j'ai envoye dans test"
        "output: <sendMessage(\"Quel est la raison ?\")>"
        "input: je voulais juste tester tes fonctionalites."
        "output: <deleteMessage channel[\"test\"] user[me] limit(2) reason(\"je voulais juste tester tes fonctionalites.\")>"
        "input: j'aimerai que tu efface les messages envoye par <@905696511197872169>"
        "output: <sendMessage(\"Pour quel raison ?\")>"
        "input: Je fais de tests. aussi sur le salon test"
        "output: <deleteMessage channel[\"test\"] user[905696511197872169] reason(\"Je fais de tests.\")>"
        "input: <@905696511197872169> a envoye beauoup trop de message en meme temps, peut tu les effacer"
        "output: <deleteMessage channel[1] user[905696511197872169] reason(\"<@905696511197872169> a envoye beauoup trop de message en meme temps\")>"
        "input: Delete the 10 messages sent before 23423424532 in all channels, The user sent too pings in a short period of time."
        "output: <sendMessage(\"To delete messages in multiple channels using before/after you need a date and time.\")>"
        "input: Delete the 10 messages sent before the 12 october 2023 in all channels, The user sent too pings in a short period of time."
        "output: <sendMessage(\"Please provide me with a time and a limit.\")>"
        "input: 12pm, 10"
        "output: <deleteMessage channel[0] before(2023-10-12 12:00:00) limit(10) reason(\"The user sent too pings in a short period of time.\")>"
        "input: Delete the 10 messages sent after the 23 january at 12am in all channels, The user sent too pings in a short period of time."
        "output: <sendMessage(\"What is the limit\")>"
        "input: 25"
        "output: <deleteMessage channel[0] after(year.now-01-23 00:00:00) limit(25) reason(\"The user sent too pings in a short period of time.\")>"
        "input: Delete the 10 messages sent after the 23 january at 12am and before 12pm in all channels, The user sent too pings in a short period of time."
        "output: <deleteMessage channel[0] after(2024-01-23 00:00:00) before(year.now-month.now-day.now 12:00:00) reason(\"The user sent too pings in a short period of time.\")>"
        "input: Delete the 10 messages sent today at 12am and before the 12 october 2023 in all channels, The user sent too pings in a short period of time."
        "output: <sendMessage(\"Please provide me with a valid time: today, tomorrow, this month, this year, this week, monday, tuesday etc... aren't valid\")>"
        "input: Delete the 10 messages sent the 12 september at 12am and before the 12 october 2023 in all channels, The user sent too pings in a short period of time."
        "output: <deleteMessage channel[0] after(2023-09-12 00:00:00) before(2023-10-12 12:00:00) reason(\"The user sent too pings in a short period of time.\")>"
        "input: Delete the 10 messages sent after 235254364 and before the 12 october 2023 in all channels, The user sent too pings in a short period of time."
        "output: <sendMessage(\"You can't use a date and time with a message id on before/after\")>"
        "input: Delete the 10 messages sent after 235254364 and before 235254365 in all channels, The user sent too pings in a short period of time."
        "output: <sendMessage(\"To delete messages in multiple channels using before/after you need a date and time.\")>"
        "input: the 12 september at 12am and before the 12 october 2023"
        "output: <deleteMessage channel[0] after(2023-09-12 00:00:00) before(2023-10-12 12:00:00) reason(\"The user sent too pings in a short period of time.\")>"
        "input: delete message sent before the 12 may of this year and after the 4 january"
        "output: <sendMessage(\"Please provide me with valid dates; you can't use this year, this month, etc..., also provide a reason\")>"
        "input: 2024, I am doing a server a cleanup"
        "output: <deleteMessage channel[1] after(2024-01-04 00:00:00) before(2024-05-12 12:00:00) reason(\"I am doing a server a cleanup\")>"
        "input: peut effacer les messages envoyer entre le 17 mai a 12h et et le 18 main 2024 a 10h35 pm"
        "output: <sendMessage(\"Quel est la raison ?\")>"
        "input: J'ai besoin de faire un nettoyage du serveur."
        "output: <deleteMessage channel[1] after(2024-05-17 12:00:00) before(2024-05-18 22:35:00) reason(\"J'ai besoin de faire un nettoyage du serveur.\")>"
        "input: peut tu effacer tout les messages envoyer entre 2h30am et 3h00am, je teste quelque chose"
        "output: <deleteMessage channel[1] after(year.now-month.now-day.now 02:30:00) before(year.now-month.now-day.now 03:00:00) reason(\"je teste quelque chose\")>"
        "input: peut-tu effacer les 10 derniers messages que j'ai envoye"
        "output: <sendMessage(\"J'ai besoin d'une raison ?\")>"
        "input: J'ai fait une erreur dans les messages envoyes."
        "output: <deleteMessage channel[1] user[1] limit(10) reason(\"J'ai fait une erreur dans les messages envoyes.\")>"
        "input: delete messages between 1241628887868506164 and 1241628917136359514"
        "output: <sendMessage(\"Please provide me with a reason\")>"
        "input: Just checking if one of your functionalities is working."
        "output: <deleteMessage after(1241628887868506164) before(1241628917136359514) reason(\"Just checking if one of your functionalities is working.\")>"
        "input: delete message between 1241628906767913031 and 1240968371143704607, I am trying to see something"
        "output: <deleteMessage after(1240968371143704607) before(1241628906767913031) reason(\"I am trying to see something\")>"
        "input: delete all messages sent in channel test and wal-i, just trying something"
        "output: deleteMessage channel[\"test\", \"wal-i\"] reason(\"just trying something\")"
        "input: delete all messages I sent in all channels"
        "output: <sendMessage(\"Please provide a reason\")>"
        "input: I am trying to see something"
        "output: <deleteMessage channel[0] user[1] reason(\"I am trying to see something\")>"
        "input: delete messages I sent in all channels"
        "output: <sendMessage(\"Please provide a reason and a limit\")>"
        "input: I am trying to see something. 10"
        "output: <deleteMessage channel[0] user[1] limit(10) reason(\"I am trying to see something\")>"
        "input: delete all messages sent by me"
        "output: <sendMessage(\"Please provide a reason\")>"
        "input: I am trying to see something"
        "output: <deleteMessage channel[1] user[1] reason(\"I am trying to see something\")>"
        "input: efface les messages que j'ai envoye"
        "output: <sendMessage(\"Pour quel raison ? Et quel est la limite\")>"
        "input: J'ai fait une erreur dans les messages envoyes. 10"
        "output: <deleteMessage channel[1] user[1] limit(10) reason(\"J'ai fait une erreur dans les messages envoyes.\")>"
        "input: efface tout les messages envoye par moi"
        "output: <sendMessage(\"Pour quel raison ?\")>"
        "input: J'ai fait une erreur dans les messages envoyes."
        "output: <deleteMessage channel[1] user[1] reason(\"J'ai fait une erreur dans les messages envoyes.\")>"
        "input: delete message between 1241688224150065193 and 1241688199340888114 in channel test, I am trying to see something"
        "output: <deleteMessage after(1241688199340888114) before(1241688224150065193) reason(\"I am trying to see something\")>"
        "input: make the following channel private"
        "output: <sendMessage(\"Please provide me with the name of the channel\")>"
        "input: RN"
        "output: <updateChannel[\"RN\"] role[\"everyone\"] removePermissons[\"read_messages\"]>"
        "input: let everyone access the following channel DF"
        "output: <updateChannel[\"DF\"] role[\"everyone\"] addPermissons[\"read_messages\"]>"
        "input: Let the role gost access the following channel DF"
        "output: <updateChannel[\"DF\"] role[\"gost\"] addPermissons[\"read_messages\"]>"
        "input: give member permission to add attachements in the following channel DF"
        "output: <updateChannel[\"DF\"] role[\"everyone\"] addPermissons[\"attach_files\"]>"
        "input: remove sali permission to send message in the following channel DF and gost"
        "output: <updateChannel[\"DF\", \"gost\"] role[\"sali\"] removePermissons[\"send_messages\", \"send_messages_in_threads\"]>"
        "input: reverse WAssap channel to private"
        "output: <updateChannel[\"WAssap\"] role[\"everyone\"] removePermissons[\"read_messages\"]>"
        "input: add the role admin to the following channel DF"
        "output: <updateChannel[\"DF\"] role[\"admin\"] addPermissons[\"read_messages\"]>"
        "input: remove the role ldfg to ali"
        "output: <editMember[\"ali\"] removeRole[\"ldfg\"]>"
        "input: add the role ldfg to ali"
        "output: <editMember[\"ali\"] addRole[\"ldfg\"]>"
        "input: mute ali"
        "output: <editMember[\"ali\"] mute>"
        "input: unmute ali"
        "output: <editMember[\"ali\"] unmute>"
        "input: ban ali"
        "output: <sendMessage(\"Please provide a reason\")>"
        "input: He insulted another member."
        "output: <editMember[\"ali\"] ban reason(\"He insulted another member.\")>"
        "input: kick ali"
        "output: <sendMessage(\"Please provide a reason\")>"
        "input: He insulted another member."
        "output: <editMember[\"ali\"] kick reason(\"He insulted another member.\")>"
        "input: Timeout ali"
        "output: <sendMessage(\"Please provide a reason and duration options are: 60 SECS, 5 MINS, 10 MINS, 1 HOUR, 1 DAY, and 1 WEEK\")>"
        "input: He insulted another member. 1 HOUR"
        "output: <editMember[\"ali\"] timeout duration(\"1 HOUR\") reason(\"He insulted another member.\")>"
        "input: mute ali soundboard"
        "output: <editMember[\"ali\"] muteSoundBoard>"
        "input: unmute ali soundboard"
        "output: <editMember[\"ali\"] unmuteSoundBoard>"
        "input: ban ali and delete the last messages he sent, he doesn't follow the rules"
        "output: <sendMessage(\"Please be precise for the message deletion part options are: Previous Hour, Previous 6 Hours, Previous 12 Hours, Previous 24 Hours, Previous 3 Days Previous 7 Days\")>"
        "input: Previous 24 Hours"
        "output: <editMember[\"ali\"] ban reason(\"he doesn't follow the rules\") deleteMessage(\"Previous 24 Hours\")>"
        "input: ban ali, he doesn't follow the rules",
        "output: <editMember[\"ali\"] ban reason(\"he doesn't follow the rules\")>"
        "input: kick ali",
        "output: <sendMessage(\"Please provide a reason\")>",
        "input: He insulted another member.",
        "output: <editMember[\"ali\"] kick reason(\"He insulted another member.\")>",
        "input: kick legarsolo"
        "output: <sendMessage(\"Please provide a reason\")>"
        "input: He insulted another member."
        "output: <editMember[\"legarsolo\"] kick reason(\"He insulted another member.\")>"
        f"input: {user_request}",
        "output: ",
    ]

    print(user_request)

    response = model.generate_content(prompt_parts)
    print(response.text)
    return response
