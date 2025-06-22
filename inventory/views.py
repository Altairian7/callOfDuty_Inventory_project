from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404


from .models import Player, Weapon, PlayerWeapon
from .serializers import (
    PlayerSerializer, WeaponSerializer, PlayerWeaponSerializer,
    UserRegistrationSerializer, LoginSerializer
)

from .tasks import send_welcome_email


# for player registration

class WeaponListView(generics.ListCreateAPIView):
    queryset = Weapon.objects.all()
    serializer_class = WeaponSerializer
    permission_classes = [IsAuthenticated]

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_player(request):
    
    serializer = UserRegisterSerializer(data=request.data)
    if serializer.is_valid():
        Player = serializer.save()
        
        if Player.email:
            send_welcome_email(Player.email, Player.username)
            
        
        refresh = RefreshToken.for_user(Player)
        return Response({
            
            'message': 'Player registered successfully',
            'Player': PlayerSerializer(Player).data,
            'tokens': {
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            }
        }, status=status.HTTP_201_CREATED)
        
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# for player login

@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_player(request):
    
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        username = serializer.validated_data['username']
        password = serializer.validated_data['password']
        
        player = authenticate(username=username, password=password)
        if player:
            refresh = RefreshToken.for_user(player)
            return Response({
                'message': 'Login successful!',
                'player': PlayerSerializer(player).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }
            })
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



# for player profiel 

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def player_profile(request):
    serializer = PlayerSerializer(request.user)
    return Response(serializer.data, status=status.HTTP_200_OK)


# for player inventory

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def player_inventory(request):
    
    inventory = PlayerWeapon.objects.filter(player=request.user)
    serializer = PlayerWeaponSerializer(inventory, many=True)
    return Response({
        'player': request.user.username,
        'total_weapons': len(inventory),
        'inventory': serializer.data
    })
    
    
# for adding weapon to player inventory

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_weapon_to_inventory(request):
  
    weapon_id = request.data.get('weapon_id')
    quantity = request.data.get('quantity', 1)
    
    if not weapon_id:
        return Response(
            {'error': 'weapon_id is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        weapon = Weapon.objects.get(id=weapon_id)
    except Weapon.DoesNotExist:
        return Response(
            {'error': 'Weapon not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )
    
    #  do the player have enough coins?
    total_cost = weapon.price * quantity
    if request.user.coins < total_cost:
        return Response(
            {'error': f'Insufficient coins. Need {total_cost}, have {request.user.coins}'}, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # wanna add a weapon to inventory or update quantity>??
    player_weapon, created = PlayerWeapon.objects.get_or_create(
        player=request.user,
        weapon=weapon,
        defaults={'quantity': quantity}
    )
    
    if not created:
        player_weapon.quantity += quantity
        player_weapon.save()
    
    # coins lost
    request.user.coins -= total_cost
    request.user.save()
    
    return Response({
        'message': f'Added {quantity} {weapon.name}(s) to inventory',
        'weapon': WeaponSerializer(weapon).data,
        'quantity': player_weapon.quantity,
        'remaining_coins': request.user.coins
    }, status=status.HTTP_201_CREATED)



# removng weapon from player inventory

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_weapon_from_inventory(request, weapon_id):
   
    try:
        player_weapon = PlayerWeapon.objects.get(
            player=request.user, 
            weapon_id=weapon_id
        )
        
        weapon_name = player_weapon.weapon.name
        player_weapon.delete()
        
        return Response({
            'message': f'Removed {weapon_name} from inventory'
        })
        
    except PlayerWeapon.DoesNotExist:
        return Response(
            {'error': 'Weapon not found in inventory'}, 
            status=status.HTTP_404_NOT_FOUND
        )
        
        
        
# simple api health check, used in my previous projects

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def health_check(request):
 
    return Response({
        'status': 'healthy',
        'message': 'COD Inventory API is running',
        'total_weapons': Weapon.objects.count(),
        'total_players': Player.objects.count()
    })