from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
from django.urls import reverse

# user model
class User(AbstractUser):
    watchlist = models.ManyToManyField('Listing', blank=True, null=True)
    
    def __str__(self):
        return f"{self.username}"

# This model will fall under the 'category' specification
class Genre(models.Model):
    name = models.CharField(max_length=32, unique=True)
    slug = models.SlugField(null=True, unique=True)
    
    def __str__(self):
        return f"{self.name}"
    
    def get_absolute_url(self):
        return reverse("model_detail", kwargs={"slug": self.slug})
    

class Listing(models.Model):
    listing_id = models.AutoField(primary_key=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="owner")
    title = models.CharField(max_length=64)
    description = models.CharField(max_length=255, verbose_name="Description")
    starting_bid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Starting Bid", validators=[MinValueValidator(Decimal('0.01'))])
    highest_bid = models.ForeignKey('Bid', on_delete=models.CASCADE, default=None, blank=True, null=True, related_name="highest_bid")
    image = models.ImageField(upload_to='media', default=None, blank=True, null=True, verbose_name="Image (Optional)")
    date = models.DateTimeField(auto_now_add=True)
    genres = models.ManyToManyField(Genre, verbose_name="Genre(s)")
    status = models.BooleanField(default=True)
        
    def __str__(self):
        return f"Listing ID: {self.listing_id} listed {self.title}"

class Bid(models.Model):
    bidder = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    bid = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="", validators=[MinValueValidator(Decimal('0.01'))], default=None)
    
    def __str__(self):
        return f"{self.bidder} bids ${self.bid}"

class Comment(models.Model):
    listing = models.ForeignKey(Listing, on_delete=models.CASCADE, default=None)
    commenter = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    comment = models.CharField(max_length=255, blank=True, null=True)
    
    def __str__(self):
        return f"User: {self.commenter} comments {self.comment}"