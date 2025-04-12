from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.db.models import Q

# Create your views here.

def home(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''

    return render(request, 'base/home.html')

def room(request):
    return HttpResponse("Room")