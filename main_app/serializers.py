from rest_framework import serializers
from .models import UserProfile, Item, Conversation, Message
from dj_rest_auth.registration.serializers import RegisterSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'

class ItemSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Item
        fields = '__all__'
        read_only_fields = ('seller',)

class MessageSerializer(serializers.ModelSerializer):
    sender = serializers.SlugRelatedField(read_only=True, slug_field='username')

    class Meta:
        model = Message
        fields = '__all__'

class ConversationSerializer(serializers.ModelSerializer):
    item_details = ItemSerializer(source='item', read_only=True)
    seller_details = serializers.SerializerMethodField()
    last_message = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'item_details', 'seller_details', 'last_message']

    def get_seller_details(self, obj):
        seller = obj.item.seller
        try:
            user_profile = UserProfile.objects.get(user=seller)
            return UserProfileSerializer(user_profile).data
        except UserProfile.DoesNotExist:
            # Return None or default values
            return None

    def get_last_message(self, obj):
        last_message = obj.message_set.last()
        return MessageSerializer(last_message).data if last_message else None
    
class CustomRegisterSerializer(RegisterSerializer):
    first_name = serializers.CharField(max_length=30, required=True)
    last_name = serializers.CharField(max_length=30, required=True)

    def save(self, request):
        user = super(CustomRegisterSerializer, self).save(request)
        print(f"Custom serializer used for user: {user.username}")
        user.first_name = self.validated_data.get('first_name', '')
        user.last_name = self.validated_data.get('last_name', '')
        user.save()
        return user