from django.db import models
from django.contrib.auth.models import AbstractUser


class Player(AbstractUser):

    telegram_username = models.CharField(max_length=256, blank=True, null=True)
    telegram_chat_id = models.CharField(max_length=51, unique=True, blank=True, null=True)
    level = models.IntegerField(default=1)
    cash = models.FloatField(default=86.35) # USD current value to INR
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.username
    
class Weapon(models.Model):
    WEAPON_TYPES = [
        ('assault_rifle', 'Assault Rifle'),
        ('submachine_gun', 'Submachine Gun'),
        ('sniper_rifle', 'Sniper Rifle'),
        ('shotgun', 'Shotgun'),
        ('pistol', 'Pistol'),
        ('launcher', 'Launcher'),
        ('melee', 'Melee'),
    ]
    
    RARITY_CHOICES = [
        ('common', 'Common'),
        ('uncommon', 'Uncommon'),
        ('rare', 'Rare'),
        ('epic', 'Epic'),
        ('legendary', 'Legendary'),
    ]
    
    name = models.CharField(max_length=105)
    weapon_type = models.CharField(max_length=54, choices=WEAPON_TYPES)
    damage = models.IntegerField()
    range = models.IntegerField()
    accuracy = models.IntegerField()
    rarity = models.CharField(max_length=57, choices=RARITY_CHOICES)
    price = models.FloatField(default=86.35)  # Price in USD 
    created_at = models.DateTimeField(auto_now_add=True)
    
    
    def __str__(self):
        return f"{self.name} ({self.weapon_type})"
    
    class Meta:
        ordering = ['rarity', 'name']
        
        
        
class PlayerWeapon(models.Model):
    player = models.ForeignKey(Player, on_delete=models.CASCADE, related_name='weapons')
    weapon = models.ForeignKey(Weapon, on_delete=models.CASCADE, related_name='players')
    quantity = models.IntegerField(default=1)
    acquired_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.player.username} - {self.weapon.name} (x{self.quantity})"
    
    class Meta:
        unique_together = ('player', 'weapon')
    
    

