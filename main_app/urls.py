from django.urls import path, re_path, include
from . import views
from rest_framework.routers import DefaultRouter
from main_app.views import ItemViewSet, UserProfileViewSet, check_token_validity


router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
    path('check-token/', check_token_validity, name='check-token-validity'),
] + router.urls 
