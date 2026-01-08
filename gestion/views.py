from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

def holamundo(request):
    return HttpResponse("xd!")

@api_view(['GET'])
@permission_classes([IsAuthenticated]) 
def dashboard_data(request):
    return Response({
        "message": f"Bienvenido al dashboard seguro, {request.user.username}",
        "stats": {
            "ventas": 125480,
            "usuarios": 45,
            "pendientes": 12
        }
    })