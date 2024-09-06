from rest_framework import serializers
from .models import UserProfile, Item, Conversation, Message, ItemImage, Favorite
from dj_rest_auth.registration.serializers import RegisterSerializer
from django.contrib.auth.models import User
from .models import create_user_profile
from django.core.validators import URLValidator
from django.core.exceptions import ValidationError

class UserProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', required=False)
    last_name = serializers.CharField(source='user.last_name', required=False)
    zip_code = serializers.CharField(required=False)

    class Meta:
        model = UserProfile
        fields = '__all__'
        extra_fields = ['username']

    def update(self, instance, validated_data):
        # Handle the nested User fields (first_name, last_name)
        user_data = validated_data.pop('user', {})
        user = instance.user
        
        # Update the User model fields
        if 'first_name' in user_data:
            user.first_name = user_data['first_name']
        if 'last_name' in user_data:
            user.last_name = user_data['last_name']
        user.save()

        # Update the UserProfile fields
        return super(UserProfileSerializer, self).update(instance, validated_data)


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
        fields = ['id', 'title', 'description', 'zip_code', 'location', 'material', 'price', 'date_posted', 'isForSale', 'isPriceNegotiable', 'category', 'seller', 'seller_profile', 'images']
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
    zip_code = serializers.CharField(max_length=12, required=True)
    profile_picture_url = serializers.URLField(required=True, allow_null=True)
    
    def validate_profile_picture_url(self, value):
        if value:
            url_validator = URLValidator()
            try:
                url_validator(value)
            except ValidationError:
                print(f"Invalid URL received: {value}")
                raise serializers.ValidationError("Enter a valid URL.")
        return value
    
    def get_cleaned_data(self):
        data = super().get_cleaned_data()
        data['zip_code'] = self.validated_data.get('zip_code', '')
        data['profile_picture_url'] = self.validated_data.get('profile_picture_url', '')
        print(f"Cleaned data: {data}")
        return data

class FavoriteSerializer(serializers.ModelSerializer):

    item = ItemSerializer(read_only=True)
    
    class Meta:
        model = Favorite
        fields = ['id', 'item']

