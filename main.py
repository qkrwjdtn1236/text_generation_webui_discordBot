import os
import discord
from discord.ext import commands
import aiohttp
import json
from httpx import Client
from datetime import datetime

url = "http://127.0.0.1:5000/v1/chat/completions"
headers = {
    "Content-Type": "application/json"
}

bot = commands.Bot(command_prefix="$", intents=discord.Intents.default())

def send_thread_message(thread, message):
    return thread.send(message)

def create_thread(ctx, message):
    thread = ctx.channel.create_thread(name=message[:15])
    send_thread_message(thread, message)
    return thread

async def generate_talk(url, headers, messages):
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json={"mode": "chat", "character": "AI", "messages": messages, "preset": "min_p_2000"}) as response:
            response.raise_for_status()
            json_response = await response.json()
            assistant_message = json_response['choices'][0]['message']['content']
            return assistant_message

def is_thread_message(message):
    return isinstance(message.channel, discord.Thread)

# Bot setup
@bot.event
async def on_ready():
    print(f'{bot.user} has connected to Discord!')

# Command definitions
@bot.command()
async def talk(ctx, *, message):
    summarized_message = message[:15]
    thread = await create_thread(ctx, message)
    await ctx.send(f"대화 시작했습니다! {thread.url}", reference=ctx.message)
    assistant_message = await generate_talk(url, headers, summarized_message)
    await thread.send(f"스레드가 성공적으로 생성되었습니다. {ctx.author.mention}님이 초대되었습니다. 다른 사람도 포함하여 초대하러면 멘션해주세요")
    await thread.send(f"질문내용: {message}")
    await thread.send(f"{ctx.author.mention}{assistant_message}")

# Error handling
@bot.event
async def on_command_error(ctx, error):
    await ctx.send('오류가 발생했습니다.')
    print(f'오류: {error}')

# Bot run
if __name__ == "__main__":
    bot.run(os.environ["LLM_BOT1"])