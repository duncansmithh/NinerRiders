from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.

rooms = [
    {'id': 1, 'name': 'Need Rides'},
    {'id': 2, 'name': 'Giving Rides'},
]

def home(request):
    context = {'rooms': rooms}
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    return render(request, 'base/home.html', context)

def room(request):
    return render(request, 'base/room.html')