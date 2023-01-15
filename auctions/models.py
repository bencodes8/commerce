from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal

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
    description = models.CharField(max_length=255, verbose_name="Description")
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Starting Bid", validators=[MinValueValidator(Decimal('0.01'))])
    image = models.ImageField(upload_to='auctions/media', default=None, blank=True, verbose_name="Image (Optional)")
    date = models.DateTimeField(auto_now_add=True)
    genre = models.ManyToManyField(Genre, default=None, related_name="genre", verbose_name="Genre(s)")
    
    def __str__(self):
        return f"Listing ID #{self.listing_id}: {self.title}, {self.date}"

class Bid(models.Model):
    pass

class Comment(models.Model):
    pass
