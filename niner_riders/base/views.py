from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.

def home(request):
    return HttpResponse("Welcome to the Niner Riders app!")

def room(request):
    return HttpResponse("Room")