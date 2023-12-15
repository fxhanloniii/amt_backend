from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Item, Conversation, Message
from .serializers import ItemSerializer, ConversationSerializer, MessageSerializer
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
    
    def perform_create(self, serializer):
        serializer.save(seller=self.request.user)

    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'description', 'location', 'material']  # Search Filters

    def get_queryset(self):
        queryset = Item.objects.all()
        category = self.request.query_params.get('category', None)
        seller = self.request.query_params.get('seller', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if seller:
            queryset = queryset.filter(seller=seller)
        
        return queryset

class UserProfileViewSet(viewsets.ModelViewSet):
    queryset = UserProfile.objects.all()
    serializer_class = UserProfileSerializer
    permission_classes = [IsUserProfileOwnerOrReadOnly]
    # Lets Add a Search filter here too



        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_token_validity(request):
    return Response({"status": "Token is valid"}, status=200)



class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer 

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer 