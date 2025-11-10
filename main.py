from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os

# --- Flaskサーバー ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!", 200

def run():
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    server = Thread(target=run)
    server.start()

# --- Discord Bot ---
intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")


# メッセージを受け取った時の処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "おやすみ":
        await message.channel.send("おやすみっす、パイセン。")
    await bot.process_commands(message)

bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")


# メッセージを受け取った時の処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if message.content == "調子どう？":
        await message.channel.send("今日も元気っすよ〜。パイセンも頑張るっすよ!")
    await bot.process_commands(message)


# Secrets に保存した TOKEN を取得
TOKEN = os.environ["TOKEN"]
import asyncio

import asyncio
import datetime

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    channel = bot.get_channel(1437049382242615379)

    while True:
        now = datetime.datetime.now()
        # 7:00ちょうどに送る
        if now.hour == 7 and now.minute == 0:
            await channel.send("おはようっすパイセン！今日もがんばるっす！🔥")
            await asyncio.sleep(60)  # 同じ1分内で連投しないように待機
        await asyncio.sleep(30)  # 30秒ごとに時間チェック
# 起動！
keep_alive()
bot.run(os.environ['TOKEN'])
