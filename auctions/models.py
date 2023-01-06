from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

class User(AbstractUser):
    def __str__(self):
        return f"{self.username}"

class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="owner")
    title = models.CharField(max_length=64)
    description = models.TextField()
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2)
    image = models.ImageField(default=None, blank=True)
    date = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Listing ID #{self.listing_id}: {self.title}, {self.date}"

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass
