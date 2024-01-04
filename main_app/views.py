from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from django.contrib.auth.models import User
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
from rest_framework.exceptions import NotFound
from rest_framework.decorators import action
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

    # Override retrieve method to get UserProfile by User ID
    @action(detail=True, url_path='user', methods=['get', 'put', 'patch'])
    def retrieve_by_user(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')  # Get user ID from URL

        # Find UserProfile by user ID
        obj = UserProfile.objects.filter(user__pk=user_id).first()

        if obj is None:
            return Response({"detail": f"A UserProfile with user ID {user_id} does not exist."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(obj)
        return Response(serializer.data)



        
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

from django.db.models import Q

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request, item_id):
    item = Item.objects.get(id=item_id)
    seller = item.seller
    buyer = request.user

    # Get or create a conversation. Consider both the item and the participants.
    conversation = Conversation.objects.filter(item=item).filter(
        Q(participants=buyer) & Q(participants=seller)
    ).first()

    if not conversation:
        conversation = Conversation.objects.create(item=item)
        conversation.participants.set([seller, buyer])

    # Handle the initial message
    initial_message = request.data.get('initialMessage')
    if initial_message:
        Message.objects.create(
            conversation=conversation,
            sender=buyer,
            text=initial_message
        )

    return Response({'conversation_id': conversation.id}, status=status.HTTP_201_CREATED)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_conversations(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user)
    serializer = ConversationSerializer(conversations, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_conversation_messages(request, conversation_id):
    try:
        conversation = Conversation.objects.get(id=conversation_id, participants=request.user)
        messages = Message.objects.filter(conversation=conversation).order_by('timestamp')
        serializer = MessageSerializer(messages, many=True)
        return Response(serializer.data)
    except Conversation.DoesNotExist:
        return Response({'error': 'Conversation not found'}, status=status.HTTP_404_NOT_FOUND)