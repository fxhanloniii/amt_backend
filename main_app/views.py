from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Item
from .serializers import ItemSerializer
from .models import UserProfile
from .serializers import UserProfileSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.permissions import AllowAny
from .permissions import IsOwnerOrReadOnly, IsUserProfileOwnerOrReadOnly
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from dj_rest_auth.registration.views import VerifyEmailView
from django.views import View
from allauth.account.views import ConfirmEmailView
from allauth.account.models import EmailConfirmation, EmailConfirmationHMAC
from django.shortcuts import get_object_or_404

# Create your views here.

class Home(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        data = {
            "message": "Hello World"
        }
        return Response(data)

class ItemViewSet(viewsets.ModelViewSet):
    queryset = Item.objects.all()
    serializer_class = ItemSerializer
    permission_classes = [IsOwnerOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'material'] # Search Filters
    # Recent posts filter?

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsUserProfileOwnerOrReadOnly]
    # Lets Add a Search filter here too



        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_token_validity(request):
    return Response({"status": "Token is valid"}, status=200)

