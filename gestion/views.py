from django.shortcuts import render
from django.http import HttpResponse

def holamundo(request):
    return HttpResponse("xd!")