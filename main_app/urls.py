from django.urls import path
from . import views
from rest_framework.routers import DefaultRouter
from main_app.views import ItemViewSet

router = DefaultRouter()
router.register(r'items', ItemViewSet)

urlpatterns = [
    path('', views.Home.as_view(), name='home'),
]
