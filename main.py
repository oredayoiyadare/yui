from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
import os
import asyncio
import datetime
import pytz
import random

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

# メッセージを受け取った時の処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 「ping」に反応
    if "ping" in message.content:
        await message.channel.send("pong")

    # 「調子どう？」に反応
    elif "調子どう" in message.content:
        await message.channel.send("今日も元気っすよ〜。パイセンも頑張るっすよ！")

    await bot.process_commands(message)

#おみくじ
@bot.command()
async def omikuji(ctx):
    fortunes = ["大吉", "中吉", "小吉", "吉", "末吉", "凶", "大凶"]
    messages = [
        "今日は最高の運勢っす！✨",
        "まあまあいい感じっすね！",
        "悪くないっすよ！",
        "油断禁物っす！",
        "ちょっと注意っすね…！",
        "うーん…今日は静かに過ごすっす。",
        "……パイセン、気をつけてっす💦"
    ]

    index = random.randint(0, len(fortunes) - 1)
    
    await ctx.send(f"🎴 パイセンの運勢は…… **{fortunes[index]}** っす！\n{messages[index]}")

@bot.command()
async def dice(ctx, num: int = 1):

    if num < 1:
        await ctx.send("少なくとも1個は振るっす！")
        return
    if num > 10:
        await ctx.send("10個以上は振れないっす！")
        return

    rolls = [random.randint(1, 6) for _ in range(num)]
    total = sum(rolls)

    if num == 1:
        await ctx.send(f"🎲 出た目は {rolls[0]}っす！")
    else:
        await ctx.send(f"🎲 出た目は {', '.join(map(str, rolls))}っす！\n合計：{total}っす！")


#じゃんけん
class JankenView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="✊ グー", style=discord.ButtonStyle.red)
    async def rock(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "グー")

    @discord.ui.button(label="✌ チョキ", style=discord.ButtonStyle.green)
    async def scissors(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "チョキ")

    @discord.ui.button(label="🖐 パー", style=discord.ButtonStyle.blurple)
    async def paper(self, interaction: discord.Interaction, button: discord.ui.Button):
        await self.play(interaction, "パー")

async def play(self, interaction, user_hand):
        hands = ["グー", "チョキ", "パー"]
        bot_hand = random.choice(hands)

        if user_hand == bot_hand:
            result = "あいこっすね！"
            color = discord.Color.yellow()
        elif (user_hand == "グー" and bot_hand == "チョキ") or \
             (user_hand == "チョキ" and bot_hand == "パー") or \
             (user_hand == "パー" and bot_hand == "グー"):
            result = "パイセンの勝ちっす！"
            color = discord.Color.green()
        else:
            result = "俺の勝ちっす！"
            color = discord.Color.red()

        embed = discord.Embed(
            title="🎲 じゃんけん結果",
            description=f"あなた：{user_hand}\n俺：{bot_hand}\n→ **{result}**",
            color=color
        )
        embed.set_footer(text="Powered by 結bot")

        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
    else:
        await interaction.response.send_message(embed=embed)
# 🕐 メッセージ削除は別アクションにする（非同期で少し待つ）
　　　　　await asyncio.sleep(1)
　　　　　try:
    　　　　　await interaction.message.delete()
　　　　　except Exception as e:
   　　　　　 print(f"メッセージ削除エラー: {e}")


@bot.command()
async def janken(ctx):
    view = JankenView()
    await ctx.send("どの手を出すっすか？", view=view)

# Secrets に保存した TOKEN を取得
TOKEN = os.environ["TOKEN"]

@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    channel = bot.get_channel(1438103528190115904)
    jst = pytz.timezone('Asia/Tokyo')

    while True:
        now = datetime.datetime.now(jst)
        # 7:00ちょうどに送る
        if now.hour == 7 and now.minute == 0:
            await channel.send("おはようっすパイセン！今日もがんばるっす！🔥")
            await asyncio.sleep(60)  # 同じ1分内で連投しないように待機
        await asyncio.sleep(30)  # 30秒ごとに時間チェック

# --- 自動再接続ラッパー ---
async def start_bot():
    while True:
        try:
            await bot.start(os.environ["TOKEN"])
        except Exception as e:
            print(f"Botが落ちたっす…再起動するっす: {e}")
            await asyncio.sleep(5)  # 少し待ってから再起動

# 起動！
keep_alive()
asyncio.run(start_bot())  # Bot起動（落ちたら再接続）