from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from main_app.views import ItemViewSet, UserProfileViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)
router.register(r'profiles', UserProfileViewSet)

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
] + router.urls 
