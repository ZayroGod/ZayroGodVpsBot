import discord
from discord.ext import commands
import json
import os
import random
import string
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# ============= CONFIGURATION FROM .env =============
BOT_TOKEN = os.getenv('BOT_TOKEN')
ADMIN_ID = int(os.getenv('ADMIN_ID'))
HOST_NAME = os.getenv('HOST_NAME', 'VantixHost')
DATA_FILE = os.getenv('DATA_FILE', 'vps_data.json')
# ===================================================

# Bot setup
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='/', intents=intents)

# Load/Save VPS data
def load_vps_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_vps_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

vps_data = load_vps_data()

@bot.event
async def on_ready():
    print(f'✅ {HOST_NAME} Bot is online!')
    print(f'🤖 Logged in as {bot.user}')
    print(f'📊 Managing {len(vps_data)} VPS instances')
    print(f'📁 Data saved in: {DATA_FILE}')

def generate_tmate():
    chars = string.ascii_letters + string.digits
    tmate_id = ''.join(random.choices(chars, k=20))
    return f"ssh {tmate_id}@sfo2.tmate.io"

def generate_sshx():
    chars = string.ascii_letters + string.digits
    sshx_id = ''.join(random.choices(chars, k=10))
    return f"https://sshx.io/s/{sshx_id}"

@bot.command(name='createvps')
async def create_vps(ctx, user_id: str):
    """Create a VPS: /createvps @username"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    user_id = user_id.replace('@', '').strip()
    vps_id = ''.join(random.choices(string.digits, k=6))
    while vps_id in vps_data:
        vps_id = ''.join(random.choices(string.digits, k=6))
    
    tmate_cmd = generate_tmate()
    sshx_link = generate_sshx()
    password = ''.join(random.choices(string.ascii_letters + string.digits, k=12))
    
    vps_data[vps_id] = {
        "owner": user_id,
        "tmate": tmate_cmd,
        "sshx": sshx_link,
        "password": password,
        "created": str(ctx.message.created_at),
        "status": "active"
    }
    save_vps_data(vps_data)
    
    embed = discord.Embed(
        title="✅ VPS Created!",
        description=f"**Host:** {HOST_NAME}\n**ID:** `{vps_id}`",
        color=discord.Color.green()
    )
    embed.add_field(name="🔑 SSH Command", value=f"```bash\n{tmate_cmd}```", inline=False)
    embed.add_field(name="🌐 Web Link", value=f"{sshx_link}", inline=False)
    embed.add_field(name="🔒 Password", value=f"```{password}```", inline=False)
    embed.set_footer(text=f"Created for @{user_id}")
    
    try:
        user = await bot.fetch_user(int(user_id))
        await user.send(embed=embed)
        await ctx.send(f"✅ VPS {vps_id} created and sent to <@{user_id}>!")
    except:
        await ctx.send(embed=embed)
        await ctx.send(f"⚠️ Could not DM <@{user_id}>. Please enable DMs.")

@bot.command(name='list')
async def list_vps(ctx):
    """List all VPS: /list"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    if not vps_data:
        await ctx.send("📭 No VPS found.")
        return

    embed = discord.Embed(
        title=f"📋 VPS List - {HOST_NAME}",
        description=f"Total: {len(vps_data)} VPS instances",
        color=discord.Color.blue()
    )
    
    for vps_id, info in list(vps_data.items())[:10]:
        embed.add_field(
            name=f"🖥️ VPS #{vps_id}",
            value=f"**Owner:** <@{info['owner']}>\n**Status:** {info['status']}",
            inline=False
        )
    
    if len(vps_data) > 10:
        embed.set_footer(text=f"Showing 10 of {len(vps_data)}. Use /view {vps_id} for details.")
    
    await ctx.send(embed=embed)

@bot.command(name='view')
async def view_vps(ctx, vps_id: str):
    """View VPS details: /view 123456"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    if vps_id not in vps_data:
        await ctx.send(f"❌ VPS #{vps_id} not found!")
        return

    info = vps_data[vps_id]
    embed = discord.Embed(
        title=f"🖥️ VPS #{vps_id} Details",
        color=discord.Color.blue()
    )
    embed.add_field(name="👤 Owner", value=f"<@{info['owner']}>", inline=True)
    embed.add_field(name="📊 Status", value=info['status'], inline=True)
    embed.add_field(name="📅 Created", value=info['created'][:19], inline=True)
    embed.add_field(name="🔑 SSH Command", value=f"```bash\n{info['tmate']}```", inline=False)
    embed.add_field(name="🌐 Web Link", value=f"{info['sshx']}", inline=False)
    embed.add_field(name="🔒 Password", value=f"```{info['password']}```", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='deletevps')
async def delete_vps(ctx, vps_id: str):
    """Delete VPS: /deletevps 123456"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    if vps_id not in vps_data:
        await ctx.send(f"❌ VPS #{vps_id} not found!")
        return

    owner = vps_data[vps_id]['owner']
    del vps_data[vps_id]
    save_vps_data(vps_data)
    await ctx.send(f"✅ VPS #{vps_id} deleted! (Owner: <@{owner}>)")

@bot.command(name='regen-ssh')
async def regen_ssh(ctx, vps_id: str):
    """Regenerate SSH: /regen-ssh 123456"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    if vps_id not in vps_data:
        await ctx.send(f"❌ VPS #{vps_id} not found!")
        return

    new_tmate = generate_tmate()
    new_sshx = generate_sshx()
    vps_data[vps_id]['tmate'] = new_tmate
    vps_data[vps_id]['sshx'] = new_sshx
    save_vps_data(vps_data)

    embed = discord.Embed(
        title="🔄 SSH Credentials Regenerated!",
        description=f"**VPS ID:** {vps_id}",
        color=discord.Color.orange()
    )
    embed.add_field(name="🔑 New SSH Command", value=f"```bash\n{new_tmate}```", inline=False)
    embed.add_field(name="🌐 New Web Link", value=f"{new_sshx}", inline=False)
    await ctx.send(embed=embed)

@bot.command(name='stop')
async def stop_vps(ctx, vps_id: str):
    """Mark VPS as stopped: /stop 123456"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    if vps_id not in vps_data:
        await ctx.send(f"❌ VPS #{vps_id} not found!")
        return

    vps_data[vps_id]['status'] = 'stopped'
    save_vps_data(vps_data)
    await ctx.send(f"⏹️ VPS #{vps_id} marked as stopped!")

@bot.command(name='start')
async def start_vps(ctx, vps_id: str):
    """Mark VPS as started: /start 123456"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    if vps_id not in vps_data:
        await ctx.send(f"❌ VPS #{vps_id} not found!")
        return

    vps_data[vps_id]['status'] = 'active'
    save_vps_data(vps_data)
    await ctx.send(f"▶️ VPS #{vps_id} marked as active!")

@bot.command(name='stats')
async def stats_cmd(ctx):
    """Show bot statistics: /stats"""
    if ctx.author.id != ADMIN_ID:
        await ctx.send("❌ Admin only!")
        return

    active = sum(1 for v in vps_data.values() if v['status'] == 'active')
    stopped = sum(1 for v in vps_data.values() if v['status'] == 'stopped')
    
    embed = discord.Embed(
        title=f"📊 {HOST_NAME} Bot Statistics",
        color=discord.Color.gold()
    )
    embed.add_field(name="📦 Total VPS", value=str(len(vps_data)), inline=True)
    embed.add_field(name="🟢 Active", value=str(active), inline=True)
    embed.add_field(name="🔴 Stopped", value=str(stopped), inline=True)
    embed.add_field(name="📁 Data File", value=DATA_FILE, inline=False)
    embed.add_field(name="👑 Admin", value=f"<@{ADMIN_ID}>", inline=False)
    embed.set_footer(text="🚀 No Docker or Proxmox required!")
    await ctx.send(embed=embed)

@bot.command(name='help')
async def help_cmd(ctx):
    """Show all commands: /help"""
    embed = discord.Embed(
        title=f"🛠️ {HOST_NAME} VPS Manager",
        description="Manage your VPS connections easily!",
        color=discord.Color.purple()
    )
    embed.add_field(
        name="📝 Commands",
        value=(
            "`/createvps @user` - Create new VPS\n"
            "`/list` - List all VPS\n"
            "`/view [id]` - View VPS details\n"
            "`/deletevps [id]` - Delete VPS\n"
            "`/regen-ssh [id]` - Regenerate SSH\n"
            "`/stop [id]` - Stop VPS\n"
            "`/start [id]` - Start VPS\n"
            "`/stats` - Bot statistics\n"
            "`/help` - Show this menu"
        ),
        inline=False
    )
    embed.set_footer(text="✅ No Docker needed! Simple & lightweight")
    await ctx.send(embed=embed)

# Error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send(f"❌ Missing argument! Use `/help` for correct usage.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send(f"❌ Invalid argument! Use `/help` for correct usage.")
    else:
        await ctx.send(f"❌ Error: {str(error)}")

# Run the bot
if __name__ == "__main__":
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found in .env file!")
        exit(1)
    bot.run(BOT_TOKEN)
