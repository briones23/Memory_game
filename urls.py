# memory_game/urls.py
from django.urls import path
from . import views

urlpatterns = [
   # Autenticación y selección de nivel
    path('', views.login_view, name='login'), 
    path('register/', views.register_view, name='register'), 
    path('select_level/', views.select_level_view, name='select_level'), 

    # Vistas principales del juego y perfil
    path('game/<str:level>/', views.game_view, name='game'), 
    path('profile/', views.profile_view, name='profile'), 
    path('logout/', views.logout_view, name='logout'), 

 
    path('game/move/', views.game_move_api, name='game_move_api'),
    
    path('game/end/<int:session_id>/', views.game_end_api, name='game_end_api'),

]