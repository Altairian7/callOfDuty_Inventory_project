from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def send_welcome_email(player_email, player_name):
    """
    Send welcome email to new player
    """
    try:
        subject = "Welcome to COD Inventory System! 🎮"
        
        message = f"""
Hello {player_name}!

Welcome to the Call of Duty Inventory Management System! 🎯

Your account has been successfully created. Here's what you can do:

🔫 Browse and collect weapons
💰 Manage your coins and purchases  
📊 Track your player level and progress
🤖 Use our Telegram bot for quick access

Getting Started:
1. Explore available weapons through our API
2. Purchase weapons using your starting coins (1000)
3. Connect with our Telegram bot for mobile access
4. Build your ultimate weapon collection!

Available Weapon Types:
• Assault Rifles (AK-74, M4A1)
• Sniper Rifles (AWP, Barrett)
• SMGs (MP5, UMP45)
• LMGs (M249, PKM)
• Shotguns (M1014, Remington)
• Pistols (Glock, Desert Eagle)

Ready to dominate the battlefield? Start building your arsenal today!

Best regards,
COD Inventory Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[player_email],
            fail_silently=False,
        )
        
        logger.info(f"Welcome email sent successfully to {player_email}")
        return f"Welcome email sent to {player_email}"
        
    except Exception as e:
        logger.error(f"Failed to send welcome email to {player_email}: {str(e)}")
        return f"Failed to send email: {str(e)}"

@shared_task
def send_weapon_purchase_confirmation(player_email, player_name, weapon_name, quantity, total_cost):
    """
    Send confirmation email when player purchases weapons
    """
    try:
        subject = f"Weapon Purchase Confirmed - {weapon_name}"
        
        message = f"""
Hello {player_name}!

Your weapon purchase has been confirmed! 🎉

Purchase Details:
• Weapon: {weapon_name}
• Quantity: {quantity}
• Total Cost: {total_cost} coins

The weapon(s) have been added to your inventory. You can view your complete arsenal through our API or Telegram bot.

Happy gaming!

COD Inventory Team
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[player_email],
            fail_silently=False,
        )
        
        logger.info(f"Purchase confirmation sent to {player_email} for {weapon_name}")
        return f"Purchase confirmation sent to {player_email}"
        
    except Exception as e:
        logger.error(f"Failed to send purchase confirmation to {player_email}: {str(e)}")
        return f"Failed to send confirmation: {str(e)}"

@shared_task
def cleanup_old_sessions():
    """
    Cleanup task to remove old/expired sessions
    """
    try:
        from django.contrib.sessions.models import Session
        from django.utils import timezone
        
        expired_sessions = Session.objects.filter(expire_date__lt=timezone.now())
        count = expired_sessions.count()
        expired_sessions.delete()
        
        logger.info(f"Cleaned up {count} expired sessions")
        return f"Cleaned up {count} expired sessions"
        
    except Exception as e:
        logger.error(f"Failed to cleanup sessions: {str(e)}")
        return f"Failed to cleanup: {str(e)}"

@shared_task
def generate_daily_stats():
    """
    Generate daily statistics for the system
    """
    try:
        from .models import Player, Weapon, PlayerWeapon
        from django.utils import timezone
        from datetime import timedelta
        
        today = timezone.now().date()
        yesterday = today - timedelta(days=1)
        
        # Get stats
        total_players = Player.objects.count()
        new_players_today = Player.objects.filter(date_joined__date=today).count()
        total_weapons = Weapon.objects.count()
        total_purchases = PlayerWeapon.objects.count()
        purchases_today = PlayerWeapon.objects.filter(acquired_at__date=today).count()
        
        stats = {
            'date': str(today),
            'total_players': total_players,
            'new_players_today': new_players_today,
            'total_weapons': total_weapons,
            'total_purchases': total_purchases,
            'purchases_today': purchases_today
        }
        
        logger.info(f"Daily stats generated: {stats}")
        return stats
        
    except Exception as e:
        logger.error(f"Failed to generate daily stats: {str(e)}")
        return f"Failed to generate stats: {str(e)}"