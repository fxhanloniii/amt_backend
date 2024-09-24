from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db.models import Avg

# Create your models here.

# User Profile Model
class UserProfile(models.Model):
    # Generic Attributes
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=30, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
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
    number_of_ratings = models.IntegerField(default=0)
    def add_rating(self, new_rating):
        total_ratings = self.ratings * self.number_of_ratings
        self.number_of_ratings += 1
        self.ratings = (total_ratings + new_rating) / self.number_of_ratings
        self.save()
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
    items_sold = models.IntegerField(default=0)  # Track individual items sold

    def increment_items_sold(self):
        self.items_sold += 1
        self.save()

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        print(f"Creating UserProfile for user: {instance.username}")
        UserProfile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    print(f"Saving UserProfile for user: {instance.username}")
    instance.userprofile.save()

# Item Model
class Item(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE, blank=True)
    title = models.CharField(max_length=100)
    description = models.TextField(max_length=500)
    location = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=12, blank=True) 
    material = models.CharField(max_length=100, blank=True)
    price = models.FloatField()
    date_posted = models.DateTimeField(auto_now_add=True)
    isForSale = models.BooleanField(default=True)
    isPriceNegotiable = models.BooleanField(default=False)
    category = models.CharField(max_length=50, blank=True)
    


class Conversation(models.Model):
    participants = models.ManyToManyField(User, related_name='conversations')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='conversations', null=False)

class Message(models.Model):
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

class ItemImage(models.Model):
    item = models.ForeignKey(Item, related_name='images', on_delete=models.CASCADE)
    image = models.URLField(max_length=200)

class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    item = models.ForeignKey(Item, on_delete=models.CASCADE, related_name='favorited_by')
    added_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'item')  

# GlobalStats model to track platform-wide data
class GlobalStats(models.Model):
    items_saved_from_landfill = models.IntegerField(default=0)  # Universal item counter

    def increment_items_sold(self):
        self.items_saved_from_landfill += 1
        self.save()

    @staticmethod
    def get_instance():
        # Ensure there is always one GlobalStats instance
        global_stats, created = GlobalStats.objects.get_or_create(id=1)
        return global_stats
