from discord.ext import commands
import requests
from random import randint
import discord
from httpx import Client
import json
from datetime import datetime
import aiohttp
import os
# from main_discord_test import get_conversation_history, create_thread, generate_talk, is_thread_message

python_file_path= os.path.dirname(os.path.abspath(__file__))

url = "http://127.0.0.1:5000/v1/chat/completions"

headers = {
    "Content-Type": "application/json"
}

channel_id = {}
history = []

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='$', intents=intents)

#############################

async def get_conversation_history(ctx,thread):
    history = await thread.fetch_messages(limit=None, before=thread.created_at)
    messages = [f"{ctx.author.name}: {message.content}" for message in history]
    return messages

async def send_thread_message(thread,message):
    await thread.send(generate_talk(url,headers,message),reference=ctx.message)

async def create_thread(ctx, message,url,headers):
    # 메시지 요약 함수
    summarized_message = message[:15]+"..."

    # 스레드 생성 및 제목 변경
    thread = await ctx.channel.create_thread(name=summarized_message)
    await send_thread_message(thread,message)

    # return thread

async def generate_talk(url, headers, message,data =
        {
        # "prompt" : "AI는 질문에 답하고, 권장 사항을 제공하고, 의사 결정을 돕도록 훈련되었습니다. AI는 사용자의 요청을 따릅니다. AI는 고정관념에서 벗어나 생각합니다.",
        "mode": "chat",
        "character": "AI",
        "messages": history,
        "preset":"min_p_2000",
        # "max_tokens": 2000
    }):
    history.append({"role": "user", "content": message})
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data, timeout=180) as response:
            response.raise_for_status()
            json_response = await response.json()
            assistant_message = json_response['choices'][0]['message']['content']
            assistant_message = assistant_message[:2000]  # 메시지 길이를 제한
            history.append({"role": "assistant", "content": assistant_message})

            return assistant_message

def is_thread_message(message):
    # 해당 메시지가 특정 스레드의 메시지인지 확인
    return isinstance(message.channel, discord.Thread)


#############################


@bot.event
async def on_ready():
    
    print(f'{bot.user} has connected to Discord!')

@bot.command()
async def talk(ctx, *,message):

    summarized_message = message[:15]+"..."

    # 스레드 생성 및 제목 변경
    thread = await ctx.channel.create_thread(name=summarized_message)

    thread_link = thread.jump_url  # 생성된 쓰레드의 링크
    await ctx.send(f"대화 시작했습니다! {thread_link}",reference=ctx.message)
    history.append({"role": "user", "content": message})
    data = {
        # "prompt" : "AI는 질문에 답하고, 권장 사항을 제공하고, 의사 결정을 돕도록 훈련되었습니다. AI는 사용자의 요청을 따릅니다. AI는 고정관념에서 벗어나 생각합니다.",
        "mode": "chat",
        "character": "AI",
        "messages": history,
        "preset":"min_p_2000",
        # "max_tokens": 2000
    }
    result = {}
    gen_text = ""
    async with aiohttp.ClientSession() as session:
        async with session.post(url, headers=headers, json=data, timeout=180) as response:
            response.raise_for_status()
            json_response = await response.json()
            assistant_message = json_response['choices'][0]['message']['content']
            assistant_message = assistant_message[:2000]  # 메시지 길이를 제한
            history.append({"role": "assistant", "content": assistant_message})
            await ctx.send('잠시후 스레드가 생성되며 대화하게 됩니다. 잠시 기다려 주세요',reference=ctx.message)
            await thread.send(f'스레드가 성공적으로 생성되었습니다. {ctx.author.mention}님이 초대되었습니다. 다른 사람도 포함하여 초대하러면 멘션해주세요')
            await thread.send(f'질문내용 : {message}')
            await thread.send(f'{ctx.author.mention}{assistant_message}')
    
@bot.command()
async def log_print(ctx):
    await ctx.send(history)

@bot.event
async def on_command_error(ctx, error):
    await ctx.send('오류가 발생했습니다.')
    print(f'오류: {error}')

@bot.event
async def before_message(ctx):
    await ctx.trigger_typing()


@bot.event
async def on_message(message):
    if message.content.startswith('$') or message.content.startswith('@'):
        await bot.process_commands(message)
        return
    if message.author == bot.user:
        return

    # 해당 메시지가 특정 스레드의 메시지인지 확인
    if is_thread_message(message):
        # print(message.content.startswith(f"<@{str(bot.user.id)}>"),message.content)
        if message.content.startswith(f"<@{str(bot.user.id)}>"):
        # if '<@!781492049090052098>' in message.content:
            messages = list(reversed([{"role": "assistant", "content": msg.content.replace(f"<@{str(bot.user.id)}>","")} if msg.author == bot.user else {"role": "user", "content": msg.content.replace(f"<@{str(bot.user.id)}>","")} async for msg in message.channel.history(limit=100)]))

            data = {
                # "prompt" : "AI는 질문에 답하고, 권장 사항을 제공하고, 의사 결정을 돕도록 훈련되었습니다. AI는 사용자의 요청을 따릅니다. AI는 고정관념에서 벗어나 생각합니다.",
                "mode": "chat",
                "character": "AI",
                "messages": messages,
                "preset":"min_p_2000",
                # "max_tokens": 2000
            }

            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=data, timeout=180) as response:
                    response.raise_for_status()
                    json_response = await response.json()
                    assistant_message = json_response['choices'][0]['message']['content']
                    assistant_message = assistant_message[:2000]  # 메시지 길이를 제한
                    await message.channel.send(assistant_message)

bot.run(os.environ["LLM_BOT1"])

