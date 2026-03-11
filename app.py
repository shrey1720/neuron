import discord
import neuron as n
from flask import Flask
import threading

app = Flask(__name__)

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

@app.route('/')
def home():
    return "Bot is running!"

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # Log incoming messages to help debugging
    print(f"Message from {message.author} in {message.channel}: {message.content}")

    # Handle commands
    if message.content.startswith('$start'):
        # Respond in the channel so the user sees it
        await message.channel.send(f'Hello {message.author.mention}! I am Neuron, a helpful assistant made by Neuralize Club to help users with Python and AI/ML.')
        # Also send a DM if that was the original intention
        await message.author.send('Hello! I am ready to help you with Python and AI/ML. You can ask me questions here or in the server.')
        
        try:
            await message.delete()
        except:
            pass
        return

    # For general messages, process with AI model
    # Note: You might want to restrict this to specific channels or DMs
    temp = await message.channel.send("I am thinking...")
    response = n.neuron(message.content)
    
    if isinstance(response, Exception):
        await message.channel.send(f"An error occurred: {str(response)}")
    elif len(response) > 2000:
        chunks = [response[i:i+2000] for i in range(0, len(response), 2000)]
        for chunk in chunks:
            await message.channel.send(chunk)
    else:
        await message.channel.send(response)

    await temp.delete()

def run_discord_bot():
    # token should be kept secret; read from env var so we don't check it into
    # source control.  the example in the repo hardcodes a dead token which
    # triggers a LoginFailure (401) when you run the script, so allow the user
    # to fix it easily.
    import os

    token = os.getenv('DISCORD_TOKEN')
    if not token:
        print('ERROR: DISCORD_TOKEN environment variable not set; bot will not start')
        return

    try:
        client.run(token)
    except Exception as exc:
        print(f"failed to start discord client: {exc}")

if __name__ == '__main__':
    # Start the Discord bot in a new thread
    threading.Thread(target=run_discord_bot).start()
    # Run the Flask app on a port provided by the environment, or 8080
    import os
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)
