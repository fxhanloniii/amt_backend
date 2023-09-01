from rest_framework import serializers
from .models import UserProfile, Item


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    seller_profile = UserProfileSerializer(source='seller.userprofile', read_only=True)  # Nested serialization
    
    class Meta:
        model = Item
        fields = '__all__'