# telegram_bot/bot.py
import os
import django
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cod_inventory.settings')
django.setup()

from inventory.models import Player, PlayerWeapon

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /start command - Register user and link Telegram account
    """
    user = update.effective_user
    chat_id = update.effective_chat.id
    
    # Check if user is already registered
    try:
        player = Player.objects.get(telegram_chat_id=str(chat_id))
        await update.message.reply_text(
            f"Welcome back, {player.username}! 🎮\n\n"
            f"Level: {player.level}\n"
            f"Coins: {player.coins}\n"
            f"Weapons: {player.weapons.count()}\n\n"
            f"Use /inventory to see your weapons!"
        )
        return
    except Player.DoesNotExist:
        pass
    
    # New user - create account or link existing
    telegram_username = user.username or user.first_name
    
    # Try to find existing player by telegram username
    try:
        player = Player.objects.get(telegram_username=telegram_username)
        player.telegram_chat_id = str(chat_id)
        player.save()
        
        await update.message.reply_text(
            f"Account linked successfully! 🎉\n\n"
            f"Welcome {player.username}!\n"
            f"Level: {player.level}\n"
            f"Coins: {player.coins}\n"
            f"Weapons: {player.weapons.count()}\n\n"
            f"Use /inventory to see your weapons!"
        )
    except Player.DoesNotExist:
        # Create new player account
        username = f"cod_{telegram_username}_{user.id}"
        player = Player.objects.create_user(
            username=username,
            telegram_username=telegram_username,
            telegram_chat_id=str(chat_id),
            first_name=user.first_name or "",
            last_name=user.last_name or ""
        )
        
        await update.message.reply_text(
            f"Welcome to COD Inventory System! 🎮\n\n"
            f"Your account has been created:\n"
            f"Username: {player.username}\n"
            f"Level: {player.level}\n"
            f"Starting Coins: {player.coins}\n\n"
            f"Visit our website to buy weapons and manage your inventory!\n"
            f"Use /inventory to see your current weapons."
        )

async def inventory_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /inventory command - Show user's weapon inventory
    """
    chat_id = update.effective_chat.id
    
    try:
        player = Player.objects.get(telegram_chat_id=str(chat_id))
        weapons = PlayerWeapon.objects.filter(player=player)
        
        if not weapons.exists():
            await update.message.reply_text(
                f"Your inventory is empty! 😔\n\n"
                f"You have {player.coins} coins to buy weapons!\n"
                f"Visit our website to purchase weapons."
            )
            return
        
        inventory_text = f"🎯 {player.username}'s Inventory\n"
        inventory_text += f"💰 Coins: {player.coins}\n"
        inventory_text += f"📊 Level: {player.level}\n\n"
        inventory_text += "🔫 Weapons:\n"
        
        for pw in weapons:
            weapon = pw.weapon
            inventory_text += f"• {weapon.name} ({weapon.weapon_type})\n"
            inventory_text += f"  Damage: {weapon.damage} | Range: {weapon.range}\n"
            inventory_text += f"  Rarity: {weapon.rarity.title()} | Qty: {pw.quantity}\n\n"
        
        await update.message.reply_text(inventory_text)
        
    except Player.DoesNotExist:
        await update.message.reply_text(
            "You're not registered yet! Use /start to create your account."
        )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /profile command - Show user profile
    """
    chat_id = update.effective_chat.id
    
    try:
        player = Player.objects.get(telegram_chat_id=str(chat_id))
        
        profile_text = f"👤 Player Profile\n\n"
        profile_text += f"🎮 Username: {player.username}\n"
        profile_text += f"📊 Level: {player.level}\n"
        profile_text += f"💰 Coins: {player.coins}\n"
        profile_text += f"🔫 Total Weapons: {player.weapons.count()}\n"
        profile_text += f"📅 Joined: {player.date_joined.strftime('%Y-%m-%d')}\n"
        
        if player.first_name:
            profile_text += f"👨‍💼 Name: {player.first_name} {player.last_name}\n"
        
        await update.message.reply_text(profile_text)
        
    except Player.DoesNotExist:
        await update.message.reply_text(
            "You're not registered yet! Use /start to create your account."
        )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Handle /help command - Show available commands
    """
    help_text = """
🎮 COD Inventory Bot Commands:

/start - Register and link your Telegram account
/inventory - View your weapon inventory
/profile - View your player profile
/help - Show this help message

🌐 Visit our website to:
• Buy new weapons
• Manage your inventory
• View all available weapons

💡 Tips:
• Earn coins by completing missions
• Collect rare weapons to increase your level
• Use the website API for full inventory management
"""
    
    await update.message.reply_text(help_text)

def main():
    """
    Main function to run the Telegram bot
    """
    # Create the Application
    application = Application.builder().token(settings.TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("inventory", inventory_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("help", help_command))

    # Run the bot
    print("🤖 COD Inventory Bot is starting...")
    print("🎮 Bot is ready to receive commands!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()