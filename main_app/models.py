from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# User Profile Model
class UserProfile(models.Model):
    # Generic Attributes
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True)
    profile_picture_url = models.URLField(max_length=200, blank=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(auto_now=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=12, blank=True)
    # Buyer-specific Attributes
    preferred_materials = models.TextField(blank=True)
    budget_range = models.CharField(max_length=100, blank=True)
    # Seller-specific Attributes
    ratings = models.FloatField(default=0.0)
    verified_seller = models.BooleanField(default=False)
    business_name = models.CharField(max_length=100, blank=True)
    materials_in_stock = models.TextField(blank=True)
    delivery_time = models.CharField(max_length=100, blank=True)
    delivery_radius = models.CharField(max_length=100, blank=True)
    # Shared Attributes for Buyers and Sellers
    wishlist = models.TextField(blank=True) # Materials of Interest
    # Other Attributes
    payment_details = models.TextField(blank=True)
    shipping_preferences = models.TextField(blank=True)
    # User Status & Roles
    is_active = models.BooleanField(default=True)
    is_seller = models.BooleanField(default=False)
    verification_status = models.CharField(max_length=50, choices=[('pending', 'Pending'), ('verified', 'Verified')], default='pending')


# Item Model
class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    location = models.CharField(max_length=100)
    material = models.CharField(max_length=100)
    price = models.FloatField()
    date_posted = models.DateTimeField(auto_now_add=True)
    is_available = models.BooleanField(default=True)
    image_url = models.URLField(max_length=200, blank=True)