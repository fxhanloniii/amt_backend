from django.urls import path, re_path, include
from . import views
from rest_framework.routers import DefaultRouter
from main_app.views import ItemViewSet, UserProfileViewSet, check_token_validity, ConversationViewSet, MessageViewSet


router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'profiles', UserProfileViewSet)
router.register(r'conversations', ConversationViewSet)
router.register(r'messages', MessageViewSet)

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('check-token/', check_token_validity, name='check-token-validity'),
] + router.urls 
