from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


# Create your views here.
class Home(APIView):
    def get(self, request):
        data = {
            "message": "Hello World"
        }
        return Response(data)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer