from flask import Flask
from threading import Thread
import discord
from discord.ext import commands
from discord.ext import tasks
import os
import asyncio
import pytz
import random
import datetime
import json

now = datetime.datetime.now()




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

# --- 勉強時間管理 ---
study_sessions = {}  # ユーザーごとに開始時間を保存する dict

@bot.command()
async def check(ctx):
    if ctx.author.id not in study_sessions:
        await ctx.send("パイセン、まだタイマー開始してないっすよ？🫠")
        return

    now = datetime.datetime.now()
    delta = now - study_sessions[ctx.author.id]
    minutes = int(delta.total_seconds() // 60)

    await ctx.send(f"今 {minutes} 分経ってるっすよ！がんばってるっすね💪🔥")

@bot.command()
async def start(ctx):
    user_id = ctx.author.id

    if user_id in study_sessions:
        await ctx.send("パイセン、もう勉強始めてるっすよ？")
        return

    study_sessions[user_id] = datetime.datetime.now()
    await ctx.send("⏱ 勉強スタートっす！気合い入れていくっすよ🔥")

@bot.command()
async def stop(ctx):
    user_id = ctx.author.id

    if user_id not in study_sessions:
        await ctx.send("まだ勉強を開始してないっすよ？")
        return

    start_time = study_sessions.pop(user_id)
    end_time = datetime.datetime.now()

    duration = end_time - start_time
    minutes = int(duration.total_seconds() // 60)

    # JSON 読み込み
    try:
        with open("study_data.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        data = {}

    # データが無い場合初期化
    if user_id not in data:
        data[user_id] = {"total": 0, "sessions": []}

    # 累計時間に加算
    data[user_id]["total"] += minutes
    data[user_id]["sessions"].append({
        "start": start_time,
        "end": end_time,
        "duration": minutes
    })
    
    # 時間に応じてメッセージ変更
    if minutes < 30:
        msg = "まだウォーミングアップっすね！ちょい短めっす！"
    elif minutes < 60:
        msg = "いいペースっすよパイセン！集中できてるっす！"
    elif minutes < 120:
        msg = "めっちゃ頑張ってるじゃないっすか…尊敬するっす！"
    else:
        msg = "パイセン…！？ もうプロの勉強家っすよ…！？"

    await ctx.send(f"⏱ 勉強終了っす！\n勉強時間：**{minutes}分**\n{msg}")

#合計時間出す
@bot.command()
async def total(ctx):
    user = str(ctx.author.id)

    try:
        with open("study_data.json", "r") as f:
            data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        await ctx.send("まだ記録がないっすね…！")
        return

    if user not in data:
        await ctx.send("パイセン、まだ1回も勉強してないっすね…？")
        return

    total_sec = data[user]["total"]
    hour = total_sec // 3600
    minute = (total_sec % 3600) // 60

    await ctx.send(f"パイセンの累計勉強時間は **{hour}時間 {minute}分** っすよ！🔥")

# メッセージを受け取った時の処理
@bot.event
async def on_message(message):
    if message.author.bot:
        return

    # 「おやすみ」に反応
    if "おやすみ" in message.content:
        await message.channel.send("おやすみっす、パイセン。")

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
            color = discord.Color.blue()
        elif (user_hand == "グー" and bot_hand == "チョキ") or \
             (user_hand == "チョキ" and bot_hand == "パー") or \
             (user_hand == "パー" and bot_hand == "グー"):
            result = "パイセンの勝ちっす！"
            color = discord.Color.green()
        else:
            result = "俺の勝ちっす！"
            color = discord.Color.red()

    # Embedの生成（↑のif文と同じ階層でOK）
        embed = discord.Embed(
            title="✊ じゃんけん結果",
            description=f"あなた：{user_hand}\n俺：{bot_hand}\n→ **{result}**",
            color=color
          )
        embed.set_footer(text="Powered by 結bot")

    # 返信の分岐（既にrespond済みかどうか）
        if interaction.response.is_done():
            await interaction.followup.send(embed=embed)
        else:
            await interaction.response.send_message(embed=embed)

    # 少し待ってから削除（非同期っす）    
        await asyncio.sleep(1)
        try:
            await interaction.message.delete()
        except Exception as e:
            print(f"メッセージ削除エラー：{e}")



@bot.command()
async def janken(ctx):
    view = JankenView()
    await ctx.send("どの手を出すっすか？", view=view)

# Secrets に保存した TOKEN を取得
TOKEN = os.environ["TOKEN"]

# グローバルフラグ
sent_today = False

# --- 定期チェックタスク ---
@tasks.loop(seconds=30)
async def check_time():
    global sent_today
    jst = pytz.timezone('Asia/Tokyo')
    now = datetime.datetime.now(jst)

    channel = bot.get_channel(1437049382242615379)
    print(f"[check_time] now={now} sent_today={sent_today} channel={channel}")


    if channel is None:
        print("[check_time] ⚠ channel is None — IDか権限を確認してください")
        return

    if now.hour == 7 and not sent_today:
        try:
            await channel.send("おはようっすパイセン！今日もがんばるっす！🔥")
            sent_today = True
            print("[check_time] メッセージ送信したっす")
        except Exception as e:
            print(f"[check_time] メッセージ送信エラー: {e}")

    # 日が変わったときにリセット（0時を採用）
    if now.hour == 0 and sent_today:
        sent_today = False
        print("[check_time] sent_today リセットしたっす")

# on_ready で1回だけ start を呼ぶ（複数回呼ばない）
@bot.event
async def on_ready():
    print(f"ログインしました: {bot.user}")
    if not check_time.is_running():
        check_time.start()
        print("check_time を start したっす")
    else:
        print("check_time は既に動いてるっす")

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