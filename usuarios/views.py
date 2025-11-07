from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegistroForm, PerfilForm


def login_view(request):
    """Vista para el login de usuarios"""
    if request.user.is_authenticated:
        # Si ya está autenticado, redirigir según el tipo de usuario
        if request.user.es_asesor():
            return redirect('citas:panel_asesor')
        return redirect('home')
    
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f'¡Bienvenido {user.get_full_name()}!')
                
                # Redirigir según el tipo de usuario
                if user.es_asesor():
                    # Asesores van al panel de asesor
                    return redirect('citas:panel_asesor')
                else:
                    # Clientes van al home o a 'next' si existe
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
        else:
            messages.error(request, 'Usuario o contraseña incorrectos.')
    else:
        form = AuthenticationForm()
    
    return render(request, 'usuarios/login.html', {'form': form})


def logout_view(request):
    """Vista para el logout de usuarios - Acepta GET y POST"""
    logout(request)
    messages.success(request, '¡Hasta pronto! Has cerrado sesión correctamente.')
    return redirect('home')


def registro_view(request):
    """Vista para el registro de nuevos usuarios"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, '¡Registro exitoso! Bienvenido al sistema.')
            return redirect('home')
    else:
        form = RegistroForm()
    
    return render(request, 'usuarios/registro.html', {'form': form})


@login_required
def perfil_view(request):
    """Vista para ver y editar el perfil del usuario"""
    if request.method == 'POST':
        form = PerfilForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Perfil actualizado correctamente.')
            return redirect('usuarios:perfil')
    else:
        form = PerfilForm(instance=request.user)
    
    return render(request, 'usuarios/perfil.html', {'form': form})