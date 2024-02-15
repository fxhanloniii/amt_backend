from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from django.contrib.auth.models import User
from .models import Item, Conversation, Message, ItemImage, Favorite
from .serializers import ItemSerializer, ConversationSerializer, MessageSerializer, CustomRegisterSerializer
from .models import UserProfile
from .serializers import UserProfileSerializer, FavoriteSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import filters
from rest_framework.decorators import parser_classes
from rest_framework.parsers import MultiPartParser, FormParser
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
from dj_rest_auth.registration.views import RegisterView
from django.db.models import Q
from django.conf import settings
import boto3
import uuid
from rest_framework.exceptions import ValidationError
# Create your views here.

class Home(APIView):
    permission_classes = [AllowAny]
    def get(self, request):
        data = {
            "message": "Hello World"
        }
        return Response(data)

class CustomRegisterView(RegisterView):
    serializer_class = CustomRegisterSerializer
    

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
        location = self.request.query_params.get('location', None)
        
        if category:
            queryset = queryset.filter(category=category)
        if seller:
            queryset = queryset.filter(seller=seller)
        if location:
            # Use Q objects for OR filtering on location, allowing for partial matches
            queryset = queryset.filter(Q(location__icontains=location))
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

    @action(detail=True, url_path='user', methods=['put', 'patch'])
    def update_by_user(self, request, *args, **kwargs):
        user_id = kwargs.get('pk')
        user_profile = UserProfile.objects.filter(user__pk=user_id).first()

        if user_profile is None:
            return Response({"detail": "UserProfile not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = self.get_serializer(user_profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def check_token_validity(request):
    return Response({"status": "Token is valid"}, status=200)



class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer 

    def get_serializer_context(self):
        return {'request': self.request}

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer 



@api_view(['POST'])
@permission_classes([IsAuthenticated])
def start_conversation(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    buyer = request.user
    seller = item.seller

    if buyer == seller:
        return Response({"error": "Cannot message yourself."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if a conversation already exists between this buyer and seller for this item
    conversation = Conversation.objects.filter(
        item=item,
        participants=buyer
    ).filter(
        participants=seller
    ).first()

    if not conversation:
        # Create a new conversation if it doesn't exist
        conversation = Conversation.objects.create(item=item)
        conversation.participants.set([buyer, seller])

    initial_message = request.data.get('initialMessage')
    if initial_message:
        Message.objects.create(conversation=conversation, sender=buyer, text=initial_message)

    return Response({'conversation_id': conversation.id}, status=status.HTTP_201_CREATED)
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_conversations(request):
    user = request.user
    conversations = Conversation.objects.filter(participants=user)
    serializer = ConversationSerializer(conversations, many=True, context={'request': request})
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
    
@api_view(['POST'])
@permission_classes([]) # Set appropriate permissions
def upload_image(request):
    print("Received request:", request.FILES)
    if 'image' not in request.FILES:
        return Response({'error': 'No image provided'}, status=status.HTTP_400_BAD_REQUEST)

    image = request.FILES['image']

    # Initialize S3 client
    s3_client = boto3.client(
        's3',
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )

    # Generate file name (could be more sophisticated)
    unique_id = uuid.uuid4()
    file_extension = image.name.split('.')[-1]
    file_name = f"uploads/{unique_id}.{file_extension}"
    

    # Upload image to S3
    try:
        s3_client.upload_fileobj(
            image,
            settings.AWS_STORAGE_BUCKET_NAME,
            file_name,
            
        )
    except Exception as e:
        print("Error uploading to S3:", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Construct URL of the uploaded file
    file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"

    # Update UserProfile with the new image URL
    try:
        user_profile = UserProfile.objects.get(user=request.user)
        user_profile.profile_picture_url = file_url
        user_profile.save()
        return Response({'image_url': file_url}, status=status.HTTP_200_OK)
    except UserProfile.DoesNotExist:
        return Response({'error': 'UserProfile not found.'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser, FormParser])
def upload_item_data_and_images(request):
    try:
        print("Received request for upload_item_data_and_images")
        # Extract item data from the request
        title = request.data.get('title')
        print(f"Title: {title}")
        description = request.data.get('description')
        location = request.data.get('location')
        price = request.data.get('price')
        isForSale = request.data.get('isForSale', 'false').lower() == 'true'
        isPriceNegotiable = request.data.get('isPriceNegotiable', 'false').lower() == 'true'
        category = request.data.get('category')
        seller = request.user

        # Save the item data (excluding images)
        item = Item(
            title=title,
            description=description,
            location=location,
            price=price,
            isForSale=isForSale,
            isPriceNegotiable=isPriceNegotiable,
            category=category,
            seller=seller,
        )
        print(f"Saving item with title: {title}, description: ...")
        item.full_clean()
        item.save()
        print("Item saved successfully.")
    
        uploaded_images = request.FILES.getlist('images')
        image_urls = []

        for image in uploaded_images:
            # Generate a unique filename for each image
            unique_id = uuid.uuid4()
            file_extension = image.name.split('.')[-1]
            file_name = f"uploads/{unique_id}.{file_extension}"
            print(f"Uploading image to S3: {file_name}")
            # Initialize S3 client
            s3_client = boto3.client(
                's3',
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
                region_name=settings.AWS_S3_REGION_NAME
            )

            # Upload image to S3
            try:
                s3_client.upload_fileobj(
                    image,
                    settings.AWS_STORAGE_BUCKET_NAME,
                    file_name,
                )
            except Exception as e:
                print("Error uploading to S3:", e)
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            # Construct URL of the uploaded file
            file_url = f"https://{settings.AWS_STORAGE_BUCKET_NAME}.s3.{settings.AWS_S3_REGION_NAME}.amazonaws.com/{file_name}"
            image_urls.append(file_url)
            print(f"Image uploaded successfully: {file_url}")
            # Create ItemImage objects to store image URLs
            item_image = ItemImage(item=item, image=file_url)
            item_image.save()

        return Response({'item_id': item.id, 'image_urls': image_urls}, status=status.HTTP_201_CREATED)
    except ValidationError as ve:
        # Handle validation errors specifically
        return Response({'error': str(ve)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        print(f"Error in upload_item_data_and_images: {e}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
class FavoriteViewSet(viewsets.ModelViewSet):
    queryset = Favorite.objects.all()
    serializer_class = FavoriteSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Favorite.objects.filter(user=user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='check/(?P<item_id>\d+)')
    def check_favorite(self, request, item_id=None):
        user = request.user
        item = get_object_or_404(Item, pk=item_id)
        favorite = Favorite.objects.filter(user=user, item=item).exists()
        return Response({'isFavorited': favorite})

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite(request, item_id):
    item = get_object_or_404(Item, id=item_id)
    favorite, created = Favorite.objects.get_or_create(user=request.user, item=item)

    if not created:
        favorite.delete()
        return Response({'status': 'removed'}, status=status.HTTP_204_NO_CONTENT)

    return Response({'status': 'added'}, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_message(request):
    
    data = request.data.copy()  
    data['sender'] = request.user.id  
    serializer = MessageSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_account(request):
    if request.method == 'DELETE':
        user = request.user
        user.delete()
        return Response({'status': 'deleted'}, status=status.HTTP_204_NO_CONTENT)
    return Response({'status': 'failed'}, status=status.HTTP_400_BAD_REQUEST)