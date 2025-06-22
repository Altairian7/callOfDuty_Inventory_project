from django.urls import path
from . import views

urlpatterns = [
    # not protected by authentication, public apis
    path('', views.health_check, name='health_check'),
    path('weapons/', views.WeaponListView.as_view(), name='weapon_list'),
    path('register/', views.register_player, name='register'),
    path('login/', views.login_player, name='login'),
    
    # those apis who are protected by authentication
    path('profile/', views.player_profile, name='player_profile'),
    path('inventory/', views.player_inventory, name='player_inventory'),
    path('inventory/add/', views.add_weapon_to_inventory, name='add_weapon'),
    path('inventory/remove/<int:weapon_id>/', views.remove_weapon_from_inventory, name='remove_weapon'),
]