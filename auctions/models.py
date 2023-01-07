from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

class Genre(models.Model):
    name = models.CharField(max_length=32, unique=True)
    
    def __str__(self):
        return f"{self.name}"

class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="owner")
    title = models.CharField(max_length=64)
    description = models.TextField(max_length=200)
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Starting Bid")
    image = models.ImageField(default=None, blank=True, verbose_name="Image (Optional)")
    date = models.DateTimeField(auto_now_add=True)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE, default=None, related_name="genre")
    
    def __str__(self):
        return f"Listing ID #{self.listing_id}: {self.title}, {self.date}"

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass
