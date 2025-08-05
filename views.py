# memory_game/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from .models import PlayerProfile, GameSession 
from django.http import JsonResponse, HttpResponseBadRequest 
import random
import json 
from django.utils import timezone 

# Vista de Login  
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('select_level') 
    else:
        form = AuthenticationForm()
    return render(request, 'memory_game/login.html', {'form': form})

# Vista de Registro
def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
           
            login(request, user)
            return redirect('select_level')
    else:
        form = UserCreationForm()
    return render(request, 'memory_game/register.html', {'form': form})

# Vista de Selección de Nivel
@login_required
def select_level_view(request):
    return render(request, 'memory_game/select_level.html')

# Vista del Juego
@login_required
def game_view(request, level):
    
    num_cards = 0
    game_time_limit = 0
    initial_attempts = 0

    if level == 'Básico':
        num_cards = 8
        game_time_limit = 60 
        initial_attempts = 10 
    elif level == 'Medio':
        num_cards = 12 
        game_time_limit = 80 
        initial_attempts = 8 
    elif level == 'Avanzado':
        num_cards = 16 
        game_time_limit = 90 
        initial_attempts = 6 
    else:
     
        return redirect('select_level')

    # Genera las cartas 
    card_values = [str(i) for i in range(1, (num_cards // 2) + 1)] * 2
    random.shuffle(card_values)

 
    game_session = GameSession.objects.create(
        player=request.user,
        level=level,
        
    )

    context = {
        'level': level,
        'initial_attempts': initial_attempts,
        'cards': card_values,
        'game_session_id': game_session.id, 
        'game_time_limit': game_time_limit, 
        
    }
    return render(request, 'memory_game/game.html', context)

# Vista del Perfil
@login_required
def profile_view(request):
    profile, _ = PlayerProfile.objects.get_or_create(user=request.user)
    profile.update_statistics()  
    game_history = GameSession.objects.filter(player=request.user).order_by('-start_time')
    context = {
        'profile': profile,
        'game_history': game_history,
    }
    return render(request, 'memory_game/profile.html', context)

# Vista de Cerrar Sesión
@login_required
def logout_view(request):
    logout(request)
    return redirect('login')

# API para la lógica de un movimiento 
def game_move_api(request):
    if request.method == 'POST' and request.user.is_authenticated:
        
        return JsonResponse({'status': 'success', 'message': 'Movimiento procesado'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido o no autenticado'}, status=400)

# API para finalizar una partida y actualizar estadísticas
def game_end_api(request, session_id):
    if request.method == 'POST':
        try:
            
            data = json.loads(request.body)
            is_won = data.get('is_won')
            duration = data.get('duration')

            
            game_session = get_object_or_404(GameSession, id=session_id, player=request.user)

         
            game_session.is_won = is_won
            game_session.end_time = timezone.now()
            game_session.duration = duration
            game_session.save()

            
            player_profile = get_object_or_404(PlayerProfile, user=request.user)
            
            #  ACTUALIZA las estadísticas del perfil
            player_profile.games_played += 1
            if is_won:
                player_profile.total_wins += 1
            else:
                player_profile.total_losses += 1 

           
            player_profile.save()

            return JsonResponse({
                'status': 'success', 
                'message': 'Sesión de juego finalizada y estadísticas actualizadas',
                'is_won': game_session.is_won,
                'duration': game_session.duration
            })
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON data in request body.")
        except Exception as e:
            
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

    return JsonResponse({'status': 'error', 'message': 'Método no permitido'}, status=405)
