import os
from dotenv import load_dotenv
import asyncio
from kafka import KafkaConsumer
from kafka import KafkaProducer

import json
from discord.ext import commands
import discord
import logging
from discord import TextChannel
import asyncio

def load_env_variable(env_key: str, fallback_env_key: str, default_value: str) -> str:
    """
    Loads an environment variable with a fallback and default value.
    Raises an exception if the default value is used.
    """
    value = os.getenv(env_key)
    if value is None:
        value = os.getenv(fallback_env_key, default_value)
        if value == default_value:
            raise Exception(f"Please set the {fallback_env_key} environment variable OR the {env_key} in the .env file"
)
    return value


load_dotenv()

DISCORD_BOT_TOKEN = load_env_variable(
    'DISCORD_BOT_TOKEN',
    'F3S_DISCORD_BOT_TOKEN',
    "my-discord-bot-token",
)
print("Start")



logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

logger = logging.getLogger(__name__)


# Initialize Discord bot
intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.reactions = True  # Enable reactions intent
intents.messages = True  # Enable messages intent, necessary to read message content

bot = commands.Bot(command_prefix="!", intents=intents)

async def is_transaction_posted(channel: TextChannel, transaction_sha256: str):
    async for message in channel.history(limit=200):  # Adjust limit as needed
        for embed in message.embeds:
            for field in embed.fields:
                if field.name == "Sha256":
                    if field.value:
                        if transaction_sha256 in field.value:
                            return True

    return False

def format_transaction_embed(transaction_data):
    embed = discord.Embed(title="Missing Transaction Alert", color=0xFF5733)  # Change color as needed
    embed.add_field(name="Sha256", value=transaction_data['transaction_sha256'], inline=False)
    embed.add_field(name="Date", value=transaction_data['date'], inline=False)
    embed.add_field(name="Amount", value=f"{transaction_data['transaction']['amount']} €", inline=True)
    embed.add_field(name="Type", value=transaction_data['transaction']['type'], inline=True)
    embed.add_field(name="Description", value=transaction_data['transaction']['description'], inline=False)
    embed.add_field(name="Source", value=transaction_data['transaction']['source_name'], inline=True)
    embed.add_field(name="Destination", value=transaction_data['transaction']['destination_name'], inline=True)
    return embed


async def kafka_missing_transactions():
    consumer = KafkaConsumer("firefly-missing", bootstrap_servers=['kafka1:9092', "kafka2:9093"], auto_offset_reset='earliest')
    loop = asyncio.get_event_loop()

    while True:
        # Non-blocking poll for Kafka messages
        records = await loop.run_in_executor(None, consumer.poll, 1.0)
        if not records or len(records) == 0:
            continue  # No records received

        for topic_partition, consumer_records in records.items():
            for record in consumer_records:
                try:
                    # Decode the message value from bytes to string and then load as JSON
                    try:
                        msg = json.loads(record.value.decode('utf-8'))
                    except Exception as e:
                        continue
                    transaction_sha256 = msg['transaction_sha256']

                    # Process each message as required
                    for guild in bot.guilds:
                        for channel in guild.text_channels:
                            if channel.name == "kafka-channel":
                                transaction_exists = await is_transaction_posted(channel, transaction_sha256)

                                if not transaction_exists:
                                    embed = format_transaction_embed(msg)
                                    sent_message = await channel.send(embed=embed)
                                    await sent_message.add_reaction("➕")
                                else:
                                    print(f"Transaction {transaction_sha256} already posted.")
                except Exception as e:
                    print(f"Error in Kafka consumer: {e}")


async def kafka_added_transactions():
    logger.info("Starting Kafka consumer for added transactions")
    consumer = KafkaConsumer("firefly-added", bootstrap_servers=['kafka1:9092', "kafka2:9093"], auto_offset_reset='earliest')
    loop = asyncio.get_event_loop()

    while True:
        # Non-blocking poll for Kafka messages
        records = await loop.run_in_executor(None, consumer.poll, 1.0)
        if not records or len(records) == 0:
            continue  # No records received

        for topic_partition, consumer_records in records.items():
            for record in consumer_records:
                try:
                    # Decode the message value from bytes to string and then load as JSON
                    try:
                        msg = json.loads(record.value.decode('utf-8'))
                    except Exception as e:
                        continue
                    transaction_sha256 = msg['transaction_sha256']

                    # Process each message as required
                    for guild in bot.guilds:
                        for channel in guild.text_channels:
                            if channel.name == "kafka-channel":

                                # Check and update messages for added transactions
                                async for discord_message in channel.history(limit=200):
                                    for embed in discord_message.embeds:
                                        for field in embed.fields:
                                            if field.name == "Sha256" and transaction_sha256 in field.value:
                                                new_embed = discord.Embed.from_dict(embed.to_dict())
                                                new_embed.title = "Added Transaction"
                                                new_embed.color = 0x00FF00  # Green color for added transactions
                                                await discord_message.edit(embed=new_embed)
                                                await discord_message.add_reaction("✅")
                                                break
                                else:
                                    continue  # Continue if the inner loop didn't break
                                break  # Break if the inner loop did break
                except Exception as e:
                    logger.error(f"Error in Kafka consumer: {e}")
            

# Event listener for reaction adds
@bot.event
async def on_reaction_add(reaction: discord.Reaction, user: discord.User):
    # Check if the reaction is on a bot's message and is a check mark
    if user != bot.user and reaction.emoji == "➕" and reaction.message.author == bot.user and "✅" not in [r.emoji for r in reaction.message.reactions]:
        transaction_sha256 = None
        for field in reaction.message.embeds[0].fields:
            if field.name == "Sha256":
                transaction_sha256 = field.value
                break

        if transaction_sha256:
            # Prepare your Kafka message
            kafka_message = {
                "event": "add_transaction",
                "transaction_sha256": transaction_sha256
            }
            # Send the event to Kafka
            producer.send('add_transaction', json.dumps(kafka_message).encode('utf-8'))

            await reaction.message.add_reaction("🔄")


# Initialize Kafka Producer
producer = KafkaProducer(bootstrap_servers=['kafka1:9092', "kafka2:9093"])

async def start():
    await bot.start(DISCORD_BOT_TOKEN)

# @bot.event
# async def on_ready():
#     print(f'Logged in as {bot.user.name} ({bot.user.id})')
#     bot.loop.create_task(kafka_missing_transactions())
#     bot.loop.create_task(kafka_added_transactions())

@bot.event
async def on_ready():
    print(f'Logged in as {bot.user.name} ({bot.user.id})')
    asyncio.create_task(kafka_missing_transactions())
    asyncio.create_task(kafka_added_transactions())


if __name__ == '__main__':
    asyncio.run(start())
    
