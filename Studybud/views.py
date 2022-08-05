from django.shortcuts import redirect, render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login, logout
from .forms import *
from django.contrib import messages
from .models import *
from django.contrib.auth.decorators import login_required

# Create your views here.
def index(request):
    q = request.GET.get('q')
    if not q:
        q = ''
    topics = Topic.objects.all()
    rooms = Room.objects.filter(name__icontains='')
    context = {
        'rooms': rooms,
        'topics': topics,
    }
    return render(request, 'Base/index.html', context)

def room(request, id):
    currentRoom = Room.objects.get(id=id)
    context = {
        'room': currentRoom,
    }
    return render(request, 'Base/room.html', context)

@login_required(login_url='login')
def createRoom(request):
    room = RoomForm()
    if request.method == 'POST':
        room = RoomForm(request.POST)
        if room.is_valid():
            form = room.save(commit=False)
            form.host = request.user
            form.save()
            return redirect('room', form.id)
    context = {
        'form': room,
    }
    return render(request, 'Base/create.html', context)

@login_required(login_url='login')
def deleteRoom(request, id):
    room = Room.objects.get(id=id)
    if request.user != room.host:
        return redirect('room', room.id)

    if request.method == 'POST':
        room.delete()
        return redirect('index')

    context = {
        'room': room,
    }
    return render(request, 'Base/delete.html', context)

@login_required(login_url='login')
def editRoom(request, id):
    room = Room.objects.get(id=id)
    form = RoomForm(instance=room)
    if request.user != room.host:
        return redirect('room', room.id)

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            newroom = form.save()
            return redirect('room', newroom.id)

    context = {
        'form': form
    }    
    return render(request, 'Base/edit.html', context)

def loginPage(request):
    form = LoginForm()
    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        email = request.POST.get('email').lower()
        password = request.POST.get('password')
        if not User.objects.filter(email=email).exists():
            messages.error(request, 'Could not find user')
            return redirect('login')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Incorrect password!')
            return redirect('index')

    context = {
        'form': form
    }
    return render(request, 'Base/login.html', context)

def registerPage(request):
    form = RegisterForm()

    context = {
        'form': form
    }

    if request.user.is_authenticated:
        return redirect('index')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        print(form.is_valid())
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.set_password(form.cleaned_data['password'])
            if User.objects.filter(username=user.username):
                messages.error(request, 'Username is already regiestered!')
                return redirect('register')
            form.save()
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, 'Email is already registered!')

    return render(request, 'Base/register.html', context) 

@login_required(login_url='login')
def logoutPage(request):
    logout(request)
    return redirect('login')
