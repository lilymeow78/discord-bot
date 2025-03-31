import discord
from discord.ext import commands
from discord import app_commands
import os
from flask import Flask, jsonify
from threading import Thread
import logging

# 1. التحقق من التوكن
TOKEN = os.environ.get('DISCORD_BOT_TOKEN')

if not TOKEN:
    print("❌ [ERROR] لم يتم العثور على `DISCORD_BOT_TOKEN` في المتغيرات البيئية.")
    raise ValueError("❌ يلزم توكن البوت!")

print(f"✅ [DEBUG] تم العثور على التوكن بنجاح: {TOKEN[:5]}...")

# 2. إعداد السجلات (Logging)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
logger = logging.getLogger("DiscordBot")

# 3. إنشاء Flask لتشغيل الموقع
app = Flask(__name__)

@app.route('/')
def home():
    return "🟢 البوت يعمل 24/7!"

# 4. إعداد بوت ديسكورد
intents = discord.Intents.default()
intents.message_content = True  

bot = commands.Bot(command_prefix="!", intents=intents)
tree = bot.tree

@app.route('/status')
def status():
    return jsonify({
        "status": "running",
        "bot_ready": bot.is_ready(),
        "latency": round(bot.latency * 1000) if bot.is_ready() else None
    })

def run_flask():
    app.run(host='0.0.0.0', port=5000, debug=False, use_reloader=False)

# 5. تشغيل البوت
@bot.event
async def on_ready():
    logger.info(f'✅ تم تسجيل الدخول باسم: {bot.user} (ID: {bot.user.id})')
    try:
        await tree.sync()
        logger.info(f'✅ تمت مزامنة {len(tree.get_commands())} أمرًا')
    except Exception as e:
        logger.error(f'❌ خطأ في مزامنة الأوامر: {e}')

@tree.command(name="ping", description="فحص سرعة البوت")
async def ping(interaction: discord.Interaction):
    latency = round(bot.latency * 1000)
    embed = discord.Embed(
        title="🏓 Pong!",
        description=f"سرعة الاستجابة: {latency}ms",
        color=discord.Color.green()
    )
    await interaction.response.send_message(embed=embed)

@tree.command(name="hello", description="رسالة ترحيبية")
async def hello(interaction: discord.Interaction):
    await interaction.response.send_message("مرحبًا بك! 👋 البوت يعمل بنجاح.")

if __name__ == "__main__":
    Thread(target=run_flask, daemon=True).start()  # تشغيل Flask في الخلفية
    try:
        bot.run(TOKEN, reconnect=True)
    except KeyboardInterrupt:
        logger.info("تم إيقاف البوت يدويًا.")
