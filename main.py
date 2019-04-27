from auth import access_token, token, api_token
from twitchio.ext import commands
from collections import deque
from datetime import datetime
import traceback
import aiohttp
import json
import sys

game_queue = {"heykatie": deque(),
              "astrokittylive": deque(),
              "adure": deque()}

with open('./channels.json', 'r+') as channels_file:
    channels = json.load(channels_file)
    channels = channels['channels']


class Botto(commands.Bot):

    def __init__(self):
        super().__init__(prefix=['!', '?'], irc_token=token, api_token=api_token,
                         nick='adure_bot', initial_channels=channels)

    async def event_ready(self):
        print(f"Logged in as {self.nick}")
        print("-----------------------\n")
        print(f"Connected to channels:..  {', '.join(self.initial_channels)}")

    async def event_message(self, message):
        print(f"{message.author.name}: {message.content}")
        await self.handle_commands(message)

    @commands.command(aliases=['join'])
    async def join_command(self, message):
        name = message.author.name
        channel = message.channel

        if name in game_queue[channel.name]:
            await channel.send(f"You are already in the queue, {name}")
            return

        game_queue[channel.name].append(name)
        await channel.send(f"{name} added to the queue!")

    @commands.command(aliases=['next'])
    async def next_command(self, message, amount = 1):
        if message.message.tags['mod'] == 1 or message.author.name == "adure":
            channel = message.channel
            counter = 0
            if amount > 1:
                while counter < amount:
                    try:
                        user = game_queue[channel.name].popleft()
                        await channel.send(f"{user}, you're up!")
                    except IndexError:
                        await channel.send("The queue is empty!")
                        return
                    finally:
                        counter += 1
                return

            try:
                user = game_queue[channel.name].popleft()
            except IndexError:
                await channel.send("The queue is empty!")
                return

            await channel.send(f"The next user is, {user}!")

    @commands.command(aliases=['remove'])
    async def remove_command(self, message, name):
        if message.message.tags['mod'] == 1 or message.author.name == "adure":
            channel = message.channel
            try:
                game_queue[channel.name].remove(name)
            except ValueError:
                await channel.send("That user is not in the queue")
                return

            await channel.send(f"{name}, removed from the queue")

    @commands.command(aliases=['queue'])
    async def queue_command(self, message):
        await message.channel.send(', '.join(list(game_queue)))

    @commands.command(aliases=['clear'])
    async def clear_command(self, message):
        if message.message.tags['mod'] == 1 or message.author.name == "adure":
            channel = message.channel
            game_queue[channel.name].clear()
            await channel.send('Game queue cleared!')

    async def event_command_error(self, ctx, error):
        if isinstance(error, commands.CommandNotFound):
            pass
        else:
            print(f"[{ctx.channel.name}] ERROR")
            traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)


bot = Botto()
bot.run()