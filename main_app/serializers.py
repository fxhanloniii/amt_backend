from rest_framework import serializers
from .models import UserProfile, Item, Conversation, Message, ItemImage, Favorite
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ItemImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ItemImage
        fields = ['id', 'image']

class MultipleItemImageSerializer(serializers.Serializer):
    image_urls = serializers.ListField(child=serializers.URLField())

class ItemSerializer(serializers.ModelSerializer):
    images = ItemImageSerializer(many=True, read_only=True)
    seller_profile = UserProfileSerializer(source='seller.userprofile', read_only=True)

    class Meta:
        model = Item
        fields = ['id', 'title', 'description', 'location', 'material', 'price', 'date_posted', 'isForSale', 'isPriceNegotiable', 'category', 'seller', 'seller_profile', 'images']
        read_only_fields = ('seller',)

class MessageSerializer(serializers.ModelSerializer):
    sender_profile = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'conversation', 'sender', 'text', 'timestamp', 'sender_profile']

    def get_sender_profile(self, obj):
        profile = UserProfile.objects.get(user=obj.sender)
        return UserProfileSerializer(profile).data
    def create(self, validated_data):
        # Create the Message instance
        # If you have nested data, handle it here before saving the Message
        message = Message.objects.create(**validated_data)
        # Handle any nested data as needed
        return message

class ConversationSerializer(serializers.ModelSerializer):
    item_details = ItemSerializer(source='item', read_only=True)
    other_user_details = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'item_details', 'other_user_details', 'last_message']

    def get_other_user_details(self, obj):
        requesting_user = self.context['request'].user
        other_user = obj.participants.exclude(id=requesting_user.id).first()

        if other_user:
            user_profile = UserProfile.objects.get(user=other_user)
            return UserProfileSerializer(user_profile).data
        return None

    def get_last_message(self, obj):
        last_message = obj.message_set.last()
        return MessageSerializer(last_message).data if last_message else None

    
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        print("CustomRegisterSerializer __init__ called")
        
    def validate(self, data):
        # Print the data received in the validate method
        print("validate data:", data)
        return super().validate(data)

    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        # Print the cleaned data
        print("cleaned data:", data)
        data['first_name'] = self.validated_data.get('first_name', '')
        data['last_name'] = self.validated_data.get('last_name', '')
        return data

    def save(self, request):
        # Print the data before saving
        cleaned_data = self.get_cleaned_data()
        print("saving data:", cleaned_data)
        user = super().save(request)
        user_profile = UserProfile.objects.get(user=user)
        user_profile.first_name = self.validated_data.get('first_name', '')
        user_profile.last_name = self.validated_data.get('last_name', '')
        user.save()
        return user

class FavoriteSerializer(serializers.ModelSerializer):

    item = ItemSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'item']

