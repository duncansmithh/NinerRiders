from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from .models import Room, Topic, Message
from .forms import RoomForm
from .forms import ClassScheduleForm
from .models import ClassSchedule
from django.shortcuts import get_object_or_404
from .forms import CustomUserCreationForm
from django.contrib.auth.forms import AuthenticationForm

# Create your views here.

# rooms = [
#     {'id': 1, 'name': 'Going to campus at 8:00 am'},
#     {'id': 2, 'name': 'Shopping at Concord Mall at 2:00 pm'},
#     {'id': 3, 'name': 'Going to the Harris Teeter at 5:00 pm'},
# ]

def loginPage(request):
    page = 'login'
    form = AuthenticationForm()

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username').lower()
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)
                return redirect('home')
            else:
                messages.error(request, 'Invalid credentials')
        else:
            messages.error(request, 'Invalid login attempt')

    return render(request, 'base/login_register.html', {'form': form, 'page': page})


def logoutUser(request):
    logout(request)
    return redirect('home')

def registerPage(request):
    form = CustomUserCreationForm()
    page = 'register'

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = user.username.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occurred during registration')

    return render(request, 'base/login_register.html', {'form': form, 'page': page})

 
def home(request):
    q = request.GET.get('q') if request.GET.get('q') else ''
    filter_type = request.GET.get('type', 'all')

    rooms = Room.objects.filter(
        Q(topic__name__icontains=q) |
        Q(name__icontains=q) |
        Q(description__icontains=q)
    )

    if filter_type == 'requested':
        rooms = rooms.filter(topic__name__iexact='Requested')
    elif filter_type == 'scheduled':
        rooms = rooms.filter(topic__name__iexact='Scheduled')

    topics = Topic.objects.all()
    room_count = rooms.count()
    room_messages = Message.objects.filter(Q(room__topic__name__icontains=q))

    context = {
        'rooms': rooms,
        'topics': topics,
        'room_count': room_count,
        'room_messages': room_messages,
        'filter': filter_type
    }
    return render(request, 'base/home.html', context)


def room(request, pk):
    room = Room.objects.get(id=pk)
    room_messages = room.message_set.all().order_by('created')
    participants = room.participants.all()
    if request.method == 'POST':
        message = Message.objects.create(
            user=request.user,
            room=room,
            body=request.POST.get('body')
        )
        room.participants.add(request.user)
        return redirect('room', pk=room.id)

    context = {'room': room, 'room_messages': room_messages, 
               'participants': participants}
    return render(request, 'base/room.html', context)

def userProfile(request, pk):
    user = User.objects.get(id=pk)
    rooms = user.room_set.all()
    room_messages = user.message_set.all()
    topics = Topic.objects.all()
    user_classes = ClassSchedule.objects.filter(user=user)
    context = {'user': user, 'rooms': rooms, 
               'room_messages': room_messages, 'topics': topics, 'user_classes': user_classes,}
    return render(request, 'base/profile.html', context)

@login_required(login_url='login')
def createRoom(request):
    form = RoomForm()

    if request.method == 'POST':
        form = RoomForm(request.POST)
        if form.is_valid():
            room = form.save(commit=False)
            room.host = request.user
            room.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def updateRoom(request, pk):
    room = Room.objects.get(id=pk)
    form = RoomForm(instance=room)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        form = RoomForm(request.POST, instance=room)
        if form.is_valid():
            form.save()
            return redirect('home')

    context = {'form': form}
    return render(request, 'base/room_form.html', context)

@login_required(login_url='login')
def deleteRoom(request, pk):
    room = Room.objects.get(id=pk)

    if request.user != room.host:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        room.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':room})

@login_required(login_url='login')
def deleteMessage(request, pk):
    message = Message.objects.get(id=pk)

    if request.user != message.user:
        return HttpResponse('You are not allowed here!!')

    if request.method == 'POST':
        message.delete()
        return redirect('home')

    return render(request, 'base/delete.html', {'obj':message})

@login_required(login_url='login')
def add_class(request):
    form = ClassScheduleForm()
    if request.method == 'POST':
        form = ClassScheduleForm(request.POST)
        if form.is_valid():
            class_obj = form.save(commit=False)
            class_obj.user = request.user
            class_obj.save()
            form.save_m2m()
            return redirect('user-profile', pk=request.user.id)
    return render(request, 'base/add_class.html', {'form': form})

@login_required(login_url='login')
def delete_class(request, pk):
    class_obj = get_object_or_404(ClassSchedule, id=pk)

    if request.user != class_obj.user:
        return HttpResponse('You are not allowed to delete this class.')

    if request.method == 'POST':
        class_obj.delete()
        return redirect('user-profile', pk=request.user.id)

    return render(request, 'base/delete.html', {'obj': class_obj})