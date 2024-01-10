from django.urls import path, re_path, include
from . import views
from rest_framework.routers import DefaultRouter
from main_app.views import ItemViewSet, UserProfileViewSet, check_token_validity, ConversationViewSet, MessageViewSet, start_conversation, get_conversation_messages, CustomRegisterView
from .views import upload_image

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('check-token/', check_token_validity, name='check-token-validity'),
    path('start-conversation/<int:item_id>/', views.start_conversation, name='start-conversation'),
    path('conversations/', views.get_user_conversations, name='user-conversations'),
    path('conversations/<int:conversation_id>/messages/', views.get_conversation_messages, name='conversation-messages'),
    path('profiles/user/<int:pk>/', UserProfileViewSet.as_view({'get': 'retrieve_by_user', 'put': 'retrieve_by_user', 'patch': 'retrieve_by_user'}), name='userprofile-by-user'),
    path('upload-image/', upload_image, name='upload-image'),
    path('upload-item-data-and-images/', views.upload_item_data_and_images, name='upload-item-data-and-images'),
    path('dj-rest-auth/registration/', CustomRegisterView.as_view(), name='rest_register'),
] + router.urls 
