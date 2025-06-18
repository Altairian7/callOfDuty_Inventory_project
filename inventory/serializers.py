from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Player, Weapon, PlayerWeapon


class WeaponSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weapon
        fields = ['id', 'name', 'weapon_type', 'damage', 'range', 'accuracy', 'rarity', 'price', 'created_at']
        
class PlayerSerializer(serializers.ModelSerializer):
    weapon_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Player
        fields = ['id', 'username', 'email', 'telegram_username', 'telegram_chat_id', 'level', 'cash', 'created_at', 'weapon_count']

        read_only_fields = ['id', 'created_at']
    def get_weapon_count(self, obj):
        return obj.weapons.count()
    
class PlayerWeaponSerializer(serializers.ModelSerializer):
    player = PlayerSerializer(read_only=True)
    Weapon_name = serializers.CharField(source='weapon.name', read_only=True)
    
    class Meta:
        model = PlayerWeapon
        fields = ['id', 'player', 'weapon', 'Weapon_name', 'quantity', 'acquired_at']
        

class UserRegistrationSerializer(serializers.ModelSerializer):
    password= serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password_confirm= serializers.CharField(write_only=True, required=True)
    
    
    class Meta:
        model = Player
        fields = ['username', 'email', 'password', 'password_confirm', 'telegram_username', 'telegram_chat_id']
    
        def validate(self, attrs):
            if attrs['password'] != attrs['password_confimr']:
                raise serializers.ValidationError("Passwords do not match")
            return attrs
        
        def create(self, validated_data):
            validated_data.pop('password_confirm')
            user = Player.objects.create_user(**validated_data)
            return user
        
        
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    

class TelegramLinkSerializer(serializers.Serializer):
    telegram_username = serializers.CharField(required=True)
    telegram_chat_id = serializers.IntegerField(required=True)

